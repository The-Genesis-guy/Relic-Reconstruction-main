#!/usr/bin/env python3
"""
Code Judging Engine for Multi-Language Support

This module provides secure code execution and judging capabilities for
competitive programming problems. It supports multiple languages with
sandboxed execution, resource limits, and comprehensive verdict reporting.

Supported Languages:
    - Python 3
    - C (GCC)
    - C++ (G++)
    - Java (JDK 11+)

Verdicts:
    - AC: Accepted (correct output)
    - WA: Wrong Answer (incorrect output)
    - CE: Compilation Error (syntax/compilation issues)
    - RE: Runtime Error (crash/exception during execution)
    - TLE: Time Limit Exceeded (execution timeout)
    - MLE: Memory Limit Exceeded (too much memory used)

Security Features:
    - Sandboxed execution in temporary directories
    - Resource limits (CPU, memory, processes, file size)
    - Timeout enforcement
    - Output size limits

Usage:
    from judge import judge_submission
    
    verdict, output = judge_submission(
        language='python',
        code='print(input())',
        test_input='Hello',
        expected_output='Hello',
        mode='stdin'
    )
"""

import subprocess
import tempfile
import shutil
import re
from pathlib import Path
from typing import Tuple, Optional

try:
    import resource
    import sys
    # Resource limits via preexec_fn are unstable on macOS with threaded apps
    RESOURCE_AVAILABLE = sys.platform != 'darwin'
except ImportError:
    # Resource module not available on Windows
    RESOURCE_AVAILABLE = False

import config

def set_resource_limits() -> None:
    """
    Set resource limits for executed code to prevent system abuse.
    
    Limits applied:
        - Memory: 256MB (configurable via config.MEMORY_LIMIT_MB)
        - CPU time: 5 seconds (configurable via config.JUDGE_TIMEOUT)
        - Processes: 10 max (prevent fork bombs)
        - File size: 10MB (prevent disk exhaustion)
    
    Note:
        Resource limits are only available on Unix-like systems.
        On Windows, this function does nothing.
    """
    if not RESOURCE_AVAILABLE:
        return
    
    try:
        # Memory limit
        memory_bytes = config.MEMORY_LIMIT_MB * 1024 * 1024
        resource.setrlimit(resource.RLIMIT_AS, (memory_bytes, memory_bytes))
        
        # Process limit (prevent fork bombs)
        resource.setrlimit(resource.RLIMIT_NPROC, (config.PROCESS_LIMIT, config.PROCESS_LIMIT))
        
        # File size limit (prevent disk exhaustion)
        file_size_bytes = config.FILE_SIZE_LIMIT_MB * 1024 * 1024
        resource.setrlimit(resource.RLIMIT_FSIZE, (file_size_bytes, file_size_bytes))
        
        # CPU time limit
        resource.setrlimit(resource.RLIMIT_CPU, (config.JUDGE_TIMEOUT, config.JUDGE_TIMEOUT))
    except (ValueError, OSError) as e:
        # Resource limits may fail in some environments (containers, etc.)
        # Log but don't crash
        import logging
        logging.warning(f"Failed to set resource limits: {e}")

def wrap_code(language: str, user_code: str, function_name: str) -> str:
    """
    Wrap user code to support function-style problems.
    
    For function-style problems, the user provides only a function definition.
    This wrapper adds the necessary boilerplate to read input, call the function,
    and write output.
    
    Args:
        language: Programming language ('python', 'c', 'cpp', 'java', 'javascript')
        user_code: User's function implementation
        function_name: Name of the function to call (default: 'solve')
    
    Returns:
        Complete executable code with wrapper
    
    Example:
        >>> code = "def solve(data): return data.upper()"
        >>> wrapped = wrap_code('python', code, 'solve')
        # Returns code that reads stdin, calls solve(), and prints result
    """
    fn = function_name or 'solve'

    if language == 'python':
        return f"""{user_code}

def __main__():
    import sys
    data = sys.stdin.read()
    result = {fn}(data)
    if result is None:
        return
    sys.stdout.write(str(result))

if __name__ == '__main__':
    __main__()
"""


    if language == 'cpp':
        return f"""#include <bits/stdc++.h>
using namespace std;

{user_code}

int main() {{
    std::ostringstream ss;
    ss << std::cin.rdbuf();
    std::string input = ss.str();
    std::string output = {fn}(input);
    std::cout << output;
    return 0;
}}
"""

    if language == 'c':
        return f"""#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_INPUT (1 << 20)

{user_code}

int main() {{
    char *input = (char *)malloc(MAX_INPUT);
    if (!input) return 1;
    size_t len = fread(input, 1, MAX_INPUT - 1, stdin);
    input[len] = '\\0';
    char *output = {fn}(input);
    if (output) {{
        fputs(output, stdout);
        free(output);
    }}
    free(input);
    return 0;
}}
"""

    if language == 'java':
        java_code = user_code
        if 'class Solution' in java_code and 'static class Solution' not in java_code:
            java_code = java_code.replace('public class Solution', 'public static class Solution', 1)
            java_code = java_code.replace('class Solution', 'static class Solution', 1)

        return f"""import java.io.*;
import java.nio.charset.StandardCharsets;

public class Main {{
{java_code}

    public static void main(String[] args) throws Exception {{
        ByteArrayOutputStream baos = new ByteArrayOutputStream();
        InputStream in = System.in;
        byte[] buf = new byte[8192];
        int n;
        while ((n = in.read(buf)) != -1) {{
            baos.write(buf, 0, n);
        }}
        String input = baos.toString(StandardCharsets.UTF_8);
        Solution sol = new Solution();
        String output = sol.{fn}(input);
        if (output != null) {{
            System.out.print(output);
        }}
    }}
}}
"""

    return user_code

def normalize_output(output: str) -> str:
    """
    Normalize output for comparison by trimming whitespace.
    
    Normalization rules:
        - Strip leading/trailing whitespace from each line
        - Strip leading/trailing whitespace from entire output
        - Normalize line endings to \\n
    
    Args:
        output: Raw output string
    
    Returns:
        Normalized output string
    """
    return '\n'.join(line.strip() for line in output.strip().split('\n'))


def truncate_output(output: str) -> str:
    """
    Truncate output if it exceeds maximum size limit.
    
    Args:
        output: Output string to truncate
    
    Returns:
        Truncated output with indicator if truncation occurred
    """
    if len(output) > config.MAX_OUTPUT_SIZE:
        return output[:config.MAX_OUTPUT_SIZE] + '\n... (output truncated)'
    return output

def ensure_bits_header(temp_dir: str) -> None:
    """
    Provide a fallback bits/stdc++.h header for environments (e.g., macOS clang/libc++)
    where the GNU convenience header is missing. Placed inside the temp directory and
    added to the include path during compilation.
    """
    bits_dir = Path(temp_dir) / 'bits'
    header_file = bits_dir / 'stdc++.h'
    if header_file.exists():
        return
    bits_dir.mkdir(parents=True, exist_ok=True)
    header_file.write_text(
        """#pragma once
#include <algorithm>
#include <array>
#include <bitset>
#include <cassert>
#include <cctype>
#include <cerrno>
#include <cfenv>
#include <cfloat>
#include <chrono>
#include <cinttypes>
#include <climits>
#include <clocale>
#include <cmath>
#include <complex>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <ctime>
#include <deque>
#include <exception>
#include <fstream>
#include <functional>
#include <iomanip>
#include <ios>
#include <iosfwd>
#include <iostream>
#include <istream>
#include <iterator>
#include <limits>
#include <list>
#include <locale>
#include <map>
#include <memory>
#include <new>
#include <numeric>
#include <ostream>
#include <queue>
#include <random>
#include <regex>
#include <set>
#include <sstream>
#include <stack>
#include <stdexcept>
#include <streambuf>
#include <string>
#include <tuple>
#include <type_traits>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <valarray>
#include <vector>
""",
        encoding='utf-8',
    )

def judge_submission(
    language: str,
    code: str,
    test_input: str,
    expected_output: str,
    mode: str = 'stdin',
    function_name: str = 'solve'
) -> Tuple[str, str]:
    """
    Execute code and return verdict by comparing output.
    
    This is the main entry point for judging submissions. It handles:
        - Code wrapping for function-style problems
        - Language-specific compilation and execution
        - Output comparison and verdict determination
        - Resource cleanup
    
    Args:
        language: Programming language ('python', 'c', 'cpp', 'java', 'javascript')
        code: Source code string
        test_input: Input to provide to the program via stdin
        expected_output: Expected output for comparison
        mode: Problem mode ('stdin' or 'function')
        function_name: Function name for function-style problems
    
    Returns:
        Tuple of (verdict, actual_output):
            - verdict: One of 'AC', 'WA', 'CE', 'RE', 'TLE'
            - actual_output: Program output or error message
    
    Example:
        >>> verdict, output = judge_submission(
        ...     'python',
        ...     'print(input().upper())',
        ...     'hello',
        ...     'HELLO'
        ... )
        >>> verdict
        'AC'
    """
    # Create temporary directory for secure execution
    temp_dir = tempfile.mkdtemp(prefix='judge_')
    
    try:
        # Wrap code for function-style problems
        if mode == 'function':
            code = wrap_code(language, code, function_name)

        # Dispatch to language-specific judge
        if language == 'python':
            return judge_python(code, test_input, expected_output, temp_dir)
        elif language == 'c':
            return judge_c(code, test_input, expected_output, temp_dir)
        elif language == 'cpp':
            return judge_cpp(code, test_input, expected_output, temp_dir)
        elif language == 'java':
            return judge_java(code, test_input, expected_output, temp_dir)
        else:
            return ('CE', f'Unsupported language: {language}')
    finally:
        # Always clean up temporary directory
        shutil.rmtree(temp_dir, ignore_errors=True)

import os
import sys

def get_python_command():
    """Detect appropriate python command."""
    if sys.platform == "win32":
        return "python"
    return "python3"

def judge_python(
    code: str,
    test_input: str,
    expected_output: str,
    temp_dir: str
) -> Tuple[str, str]:
    """
    Judge Python code submission.
    """
    code_file = Path(temp_dir) / 'solution.py'
    code_file.write_text(code, encoding='utf-8', errors='replace')
    
    py_cmd = get_python_command()
    
    try:
        # On Windows, we need creationflags to prevent new console windows if running as service
        creationflags = 0
        if sys.platform == "win32":
            creationflags = getattr(subprocess, 'CREATE_NO_WINDOW', 0)

        result = subprocess.run(
            [py_cmd, str(code_file)],
            input=test_input,
            capture_output=True,
            text=True,
            timeout=config.JUDGE_TIMEOUT,
            cwd=temp_dir,
            preexec_fn=set_resource_limits if RESOURCE_AVAILABLE else None,
            creationflags=creationflags
        )
        
        if result.returncode != 0:
            return ('RE', truncate_output(result.stderr))
        
        stdout = truncate_output(result.stdout)
        actual = normalize_output(stdout)
        expected = normalize_output(expected_output)
        
        return ('AC', actual) if actual == expected else ('WA', actual)
            
    except subprocess.TimeoutExpired:
        return ('TLE', 'Time Limit Exceeded')
    except Exception as e:
        import traceback
        return ('RE', f"Internal Error: {str(e)}\n{traceback.format_exc()}")


def judge_c(
    code: str,
    test_input: str,
    expected_output: str,
    temp_dir: str
) -> Tuple[str, str]:
    """Judge C code submission."""
    code_file = Path(temp_dir) / 'solution.c'
    exe_file = Path(temp_dir) / 'solution'
    code_file.write_text(code, encoding='utf-8', errors='replace')
    
    # Compilation phase
    try:
        compile_result = subprocess.run(
            ['gcc', str(code_file), '-o', str(exe_file), '-lm'],
            capture_output=True,
            text=True,
            timeout=config.JUDGE_TIMEOUT,
            cwd=temp_dir
        )
        
        if compile_result.returncode != 0:
            return ('CE', compile_result.stderr)
    except subprocess.TimeoutExpired:
        return ('CE', 'Compilation timeout')
    except Exception as e:
        return ('CE', str(e))
    
    # Execute
    try:
        creationflags = 0
        if sys.platform == "win32":
            creationflags = getattr(subprocess, 'CREATE_NO_WINDOW', 0)

        result = subprocess.run(
            [str(exe_file)],
            input=test_input,
            capture_output=True,
            text=True,
            timeout=config.JUDGE_TIMEOUT,
            cwd=temp_dir,
            preexec_fn=set_resource_limits if RESOURCE_AVAILABLE else None,
            creationflags=creationflags
        )
        
        if result.returncode != 0:
            return ('RE', result.stderr)
        
        actual = normalize_output(result.stdout)
        expected = normalize_output(expected_output)
        
        if actual == expected:
            return ('AC', actual)
        else:
            return ('WA', actual)
            
    except subprocess.TimeoutExpired:
        return ('TLE', 'Time Limit Exceeded')
    except Exception as e:
        return ('RE', str(e))

def judge_cpp(
    code: str,
    test_input: str,
    expected_output: str,
    temp_dir: str
) -> Tuple[str, str]:
    """Judge C++ code submission."""
    code_file = Path(temp_dir) / 'solution.cpp'
    exe_file = Path(temp_dir) / 'solution'
    code_file.write_text(code, encoding='utf-8', errors='replace')
    
    # Provide fallback bits/stdc++.h for macOS/clang environments
    ensure_bits_header(temp_dir)
    
    # Compilation phase
    try:
        compile_result = subprocess.run(
            ['g++', str(code_file),
             '-I', temp_dir,
             '-I', str(Path(temp_dir) / 'bits'),
             '-o', str(exe_file), '-std=c++17'],
            capture_output=True,
            text=True,
            timeout=config.JUDGE_TIMEOUT,
            cwd=temp_dir
        )
        
        if compile_result.returncode != 0:
            return ('CE', compile_result.stderr)
    except subprocess.TimeoutExpired:
        return ('CE', 'Compilation timeout')
    except Exception as e:
        return ('CE', str(e))
    
    # Execute
    try:
        creationflags = 0
        if sys.platform == "win32":
            creationflags = getattr(subprocess, 'CREATE_NO_WINDOW', 0)

        result = subprocess.run(
            [str(exe_file)],
            input=test_input,
            capture_output=True,
            text=True,
            timeout=config.JUDGE_TIMEOUT,
            cwd=temp_dir,
            preexec_fn=set_resource_limits if RESOURCE_AVAILABLE else None,
            creationflags=creationflags
        )
        
        if result.returncode != 0:
            return ('RE', result.stderr)
        
        actual = normalize_output(result.stdout)
        expected = normalize_output(expected_output)
        
        if actual == expected:
            return ('AC', actual)
        else:
            return ('WA', actual)
            
    except subprocess.TimeoutExpired:
        return ('TLE', 'Time Limit Exceeded')
    except Exception as e:
        return ('RE', str(e))

def judge_java(
    code: str,
    test_input: str,
    expected_output: str,
    temp_dir: str
) -> Tuple[str, str]:
    """Judge Java code submission."""
    # Extract public class name from code
    match = re.search(r'public\s+class\s+(\w+)', code)
    if not match:
        return ('CE', 'No public class found in Java code')
    
    class_name = match.group(1)
    code_file = Path(temp_dir) / f'{class_name}.java'
    code_file.write_text(code, encoding='utf-8', errors='replace')
    
    # Compilation phase
    try:
        compile_result = subprocess.run(
            ['javac', str(code_file)],
            capture_output=True,
            text=True,
            timeout=config.JUDGE_TIMEOUT,
            cwd=temp_dir
        )
        
        if compile_result.returncode != 0:
            return ('CE', truncate_output(compile_result.stderr))
    except subprocess.TimeoutExpired:
        return ('CE', 'Compilation timeout')
    except Exception as e:
        return ('CE', str(e))
    
    # Execution phase
    try:
        creationflags = 0
        if sys.platform == "win32":
            creationflags = getattr(subprocess, 'CREATE_NO_WINDOW', 0)

        result = subprocess.run(
            ['java', class_name],
            input=test_input,
            capture_output=True,
            text=True,
            timeout=config.JUDGE_TIMEOUT,
            cwd=temp_dir,
            preexec_fn=set_resource_limits if RESOURCE_AVAILABLE else None,
            creationflags=creationflags
        )
        
        if result.returncode != 0:
            return ('RE', truncate_output(result.stderr))
        
        actual = normalize_output(result.stdout)
        expected = normalize_output(expected_output)
        
        return ('AC', actual) if actual == expected else ('WA', actual)
            
    except subprocess.TimeoutExpired:
        return ('TLE', 'Time Limit Exceeded')
    except Exception as e:
        return ('RE', str(e))

#!/usr/bin/env python3
"""
Convert existing description.txt and testcases.txt files to JSON format.
Useful for editing existing questions or creating templates from existing problems.
"""

import os
import sys
import json
import re

def parse_description(desc_file):
    """Parse description.txt file"""
    with open(desc_file, 'r') as f:
        content = f.read()
    
    data = {}
    
    # Extract fields using regex
    patterns = {
        'title': r'Problem Title:\s*(.+)',
        'contest': r'Contest:\s*(.+)',
        'problem_type': r'Problem Type:\s*(.+)',
        'problem_mode': r'Problem Mode:\s*(.+)',
        'total_marks': r'Total Marks:\s*(\d+)',
    }
    
    for key, pattern in patterns.items():
        match = re.search(pattern, content)
        if match:
            data[key] = match.group(1).strip()
    
    # Extract multi-line sections
    constraints_match = re.search(r'Constraints:\s*\n(.+?)\n\nDescription:', content, re.DOTALL)
    if constraints_match:
        data['constraints'] = constraints_match.group(1).strip()
    
    description_match = re.search(r'Description:\s*\n(.+?)\n\nInput Format:', content, re.DOTALL)
    if description_match:
        data['description'] = description_match.group(1).strip()
    
    input_format_match = re.search(r'Input Format:\s*\n(.+?)\n\nOutput Format:', content, re.DOTALL)
    if input_format_match:
        data['input_format'] = input_format_match.group(1).strip()
    
    output_format_match = re.search(r'Output Format:\s*\n(.+?)$', content, re.DOTALL)
    if output_format_match:
        data['output_format'] = output_format_match.group(1).strip()
    
    return data

def parse_testcases(testcases_file):
    """Parse testcases.txt file"""
    with open(testcases_file, 'r') as f:
        content = f.read()
    
    test_cases = []
    lines = content.split('\n')
    i = 0
    
    while i < len(lines):
        if lines[i].startswith('# Test Case'):
            # Parse test case header
            header = lines[i]
            
            # Determine type and points
            if 'Sample' in header:
                tc_type = 'Sample'
                points = 0
            else:
                tc_type = 'Hidden'
                points = 'auto'
            
            i += 1
            
            # Find INPUT:
            while i < len(lines) and not lines[i].startswith('INPUT:'):
                i += 1
            
            if i >= len(lines):
                break
            
            i += 1  # Skip INPUT: line
            
            # Collect input lines until OUTPUT:
            input_lines = []
            while i < len(lines) and not lines[i].startswith('OUTPUT:'):
                input_lines.append(lines[i])
                i += 1
            
            if i >= len(lines):
                break
            
            i += 1  # Skip OUTPUT: line
            
            # Collect output lines until next test case or end
            output_lines = []
            while i < len(lines) and not lines[i].startswith('# Test Case'):
                if lines[i].strip():  # Only add non-empty lines
                    output_lines.append(lines[i])
                i += 1
            
            test_input = '\n'.join(input_lines).strip()
            test_output = '\n'.join(output_lines).strip()
            
            test_cases.append({
                'type': tc_type,
                'points': points,
                'input': test_input,
                'output': test_output
            })
        else:
            i += 1
    
    return test_cases

def read_solution_files(problem_dir):
    """Read solution files from Solution or Solutions folder"""
    solutions = {}
    
    # Check both Solution and Solutions folders
    solution_dirs = [
        os.path.join(problem_dir, 'Solution'),
        os.path.join(problem_dir, 'Solutions')
    ]
    
    for solution_dir in solution_dirs:
        if os.path.exists(solution_dir):
            # Look for solution files
            for filename in os.listdir(solution_dir):
                filepath = os.path.join(solution_dir, filename)
                
                # Only read code files
                if filename.endswith(('.py', '.java', '.cpp', '.c', '.js', '.go')):
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Determine language from extension
                        ext = filename.split('.')[-1]
                        lang_map = {
                            'py': 'python',
                            'java': 'java',
                            'cpp': 'cpp',
                            'c': 'c',
                            'js': 'javascript',
                            'go': 'go'
                        }
                        
                        lang = lang_map.get(ext, ext)
                        solutions[lang] = content
                    except Exception as e:
                        print(f"Warning: Could not read {filename}: {e}")
    
    return solutions

def read_starter_code(problem_dir):
    """Read starter code files from starter_code folder"""
    starter_codes = {}
    
    starter_dir = os.path.join(problem_dir, 'starter_code')
    
    if os.path.exists(starter_dir):
        for filename in os.listdir(starter_dir):
            filepath = os.path.join(starter_dir, filename)
            
            # Only read code files
            if filename.endswith(('.py', '.java', '.cpp', '.c', '.js', '.go')):
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Determine language from extension
                    ext = filename.split('.')[-1]
                    lang_map = {
                        'py': 'python',
                        'java': 'java',
                        'cpp': 'cpp',
                        'c': 'c',
                        'js': 'javascript',
                        'go': 'go'
                    }
                    
                    lang = lang_map.get(ext, ext)
                    starter_codes[lang] = content
                except Exception as e:
                    print(f"Warning: Could not read starter {filename}: {e}")
    
    return starter_codes

def convert_to_json(problem_dir, output_file=None):
    """Convert problem directory to JSON"""
    
    desc_file = os.path.join(problem_dir, 'description.txt')
    testcases_file = os.path.join(problem_dir, 'testcases.txt')
    
    if not os.path.exists(desc_file):
        print(f"Error: {desc_file} not found")
        return None
    
    # Parse description
    data = parse_description(desc_file)
    
    # Add folder name
    folder_name = os.path.basename(problem_dir.rstrip('/'))
    data['folder_name'] = folder_name
    
    # Parse test cases if available
    if os.path.exists(testcases_file):
        data['test_cases'] = parse_testcases(testcases_file)
    
    # Read solution files
    solutions = read_solution_files(problem_dir)
    if solutions:
        data['solutions'] = solutions
    
    # Read starter code files
    starter_codes = read_starter_code(problem_dir)
    if starter_codes:
        data['starter_code'] = starter_codes
    
    # Write to file or stdout
    if output_file:
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"✅ Converted to JSON: {output_file}")
    else:
        print(json.dumps(data, indent=2))
    
    return data

def main():
    """Entry point"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 convert_to_json.py <problem_directory> [output.json]")
        print("\nExample:")
        print("  python3 convert_to_json.py round1_full_pack_optionA_solutions/E1_Palindrome_Checker/ e1.json")
        print("\nOr print to stdout:")
        print("  python3 convert_to_json.py round1_full_pack_optionA_solutions/E1_Palindrome_Checker/")
        sys.exit(1)
    
    problem_dir = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(problem_dir):
        print(f"Error: Directory '{problem_dir}' not found")
        sys.exit(1)
    
    try:
        convert_to_json(problem_dir, output_file)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()

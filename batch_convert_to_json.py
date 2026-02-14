#!/usr/bin/env python3
"""
Batch convert all questions in a folder to JSON files.
Processes all subdirectories containing description.txt files.
"""

import os
import sys
import json
import re
from pathlib import Path

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
                        print(f"   Warning: Could not read {filename}: {e}")
    
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
                    print(f"   Warning: Could not read starter {filename}: {e}")
    
    return starter_codes

def convert_problem_to_json(problem_dir):
    """Convert a single problem directory to JSON"""
    
    desc_file = os.path.join(problem_dir, 'description.txt')
    testcases_file = os.path.join(problem_dir, 'testcases.txt')
    
    if not os.path.exists(desc_file):
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
    
    return data

def batch_convert(source_dir, output_dir=None, single_file=False):
    """
    Batch convert all problems in a directory
    
    Args:
        source_dir: Directory containing problem folders
        output_dir: Directory to save JSON files (default: source_dir/json_output)
        single_file: If True, save all questions in one JSON file
    """
    
    if not os.path.exists(source_dir):
        print(f"❌ Error: Directory '{source_dir}' not found")
        return
    
    # Find all subdirectories with description.txt
    problem_dirs = []
    for item in sorted(os.listdir(source_dir)):
        item_path = os.path.join(source_dir, item)
        if os.path.isdir(item_path):
            desc_file = os.path.join(item_path, 'description.txt')
            if os.path.exists(desc_file):
                problem_dirs.append(item_path)
    
    if not problem_dirs:
        print(f"❌ No problem directories found in '{source_dir}'")
        print("   (Looking for folders containing description.txt)")
        return
    
    print(f"📁 Found {len(problem_dirs)} problem(s) to convert\n")
    
    # Set output directory
    if output_dir is None:
        output_dir = os.path.join(source_dir, 'json_output')
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Convert all problems
    all_problems = []
    success_count = 0
    fail_count = 0
    
    for problem_dir in problem_dirs:
        problem_name = os.path.basename(problem_dir)
        
        try:
            data = convert_problem_to_json(problem_dir)
            
            if data:
                all_problems.append(data)
                
                if not single_file:
                    # Save individual JSON file
                    output_file = os.path.join(output_dir, f"{problem_name}.json")
                    with open(output_file, 'w') as f:
                        json.dump(data, f, indent=2)
                    
                    test_count = len(data.get('test_cases', []))
                    solution_count = len(data.get('solutions', {}))
                    starter_count = len(data.get('starter_code', {}))
                    
                    print(f"✅ {problem_name}")
                    print(f"   → {output_file}")
                    print(f"   → {test_count} test cases")
                    if solution_count > 0:
                        langs = ', '.join(data['solutions'].keys())
                        print(f"   → {solution_count} solution(s): {langs}")
                    if starter_count > 0:
                        langs = ', '.join(data['starter_code'].keys())
                        print(f"   → {starter_count} starter code(s): {langs}")
                    print()
                
                success_count += 1
            else:
                print(f"⚠️  {problem_name}: Could not parse")
                fail_count += 1
                
        except Exception as e:
            print(f"❌ {problem_name}: Error - {e}\n")
            fail_count += 1
    
    # Save single file if requested
    if single_file and all_problems:
        output_file = os.path.join(output_dir, 'all_questions.json')
        with open(output_file, 'w') as f:
            json.dump(all_problems, f, indent=2)
        print(f"\n📦 All questions saved to: {output_file}")
    
    # Summary
    print("=" * 60)
    print(f"✅ Successfully converted: {success_count}")
    if fail_count > 0:
        print(f"❌ Failed: {fail_count}")
    print(f"📁 Output directory: {output_dir}")
    print("=" * 60)

def main():
    """Entry point"""
    if len(sys.argv) < 2:
        print("Batch Convert Questions to JSON")
        print("=" * 60)
        print("\nUsage:")
        print("  python3 batch_convert_to_json.py <source_directory> [output_directory] [--single-file]")
        print("\nExamples:")
        print("  # Convert all questions, save as individual JSON files")
        print("  python3 batch_convert_to_json.py round1_full_pack_optionA_solutions/")
        print()
        print("  # Specify output directory")
        print("  python3 batch_convert_to_json.py round1_full_pack_optionA_solutions/ json_backup/")
        print()
        print("  # Save all questions in a single JSON file")
        print("  python3 batch_convert_to_json.py round1_full_pack_optionA_solutions/ --single-file")
        print()
        print("Options:")
        print("  --single-file    Save all questions in one JSON file (all_questions.json)")
        print()
        sys.exit(1)
    
    source_dir = sys.argv[1]
    output_dir = None
    single_file = False
    
    # Parse arguments
    for i in range(2, len(sys.argv)):
        if sys.argv[i] == '--single-file':
            single_file = True
        elif output_dir is None:
            output_dir = sys.argv[i]
    
    try:
        batch_convert(source_dir, output_dir, single_file)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()

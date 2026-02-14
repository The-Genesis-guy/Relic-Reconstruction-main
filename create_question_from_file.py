#!/usr/bin/env python3
"""
Script to create question files from a JSON configuration file.
This is useful for batch creation or when you have the data prepared.
"""

import json
import os
import sys

def load_config(config_file):
    """Load question configuration from JSON file"""
    with open(config_file, 'r') as f:
        return json.load(f)

def generate_description_file(data):
    """Generate description.txt content"""
    content = f"""Problem Title: {data['title']}
Contest: {data['contest']}
Problem Type: {data['problem_type']}
Problem Mode: {data['problem_mode']}
Total Marks: {data['total_marks']}

Constraints:
{data['constraints']}

Description:
{data['description']}

Input Format:
{data['input_format']}

Output Format:
{data['output_format']}
"""
    return content

def generate_testcases_file(test_cases):
    """Generate testcases.txt content"""
    lines = []
    
    for i, tc in enumerate(test_cases, 1):
        tc_type = tc.get('type', 'Sample')
        points = tc.get('points', 0)
        
        if points == 'auto' or points == 0:
            if tc_type == 'Sample':
                points_str = "0 points"
            else:
                points_str = "will get auto points"
        else:
            points_str = f"{points} points"
        
        lines.append(f"# Test Case {i} ({tc_type}) - {points_str}")
        lines.append("INPUT:")
        lines.append(tc['input'].rstrip())
        lines.append("OUTPUT:")
        lines.append(tc['output'].rstrip())
        lines.append("")  # Empty line between test cases
    
    return '\n'.join(lines).rstrip() + '\n'

def create_question_from_config(config_file, output_dir=None):
    """Create question files from configuration"""
    
    # Load configuration
    config = load_config(config_file)
    
    # Extract data
    title = config['title']
    folder_name = config.get('folder_name', title.replace(' ', '_'))
    
    # Create output directory
    if output_dir:
        full_path = os.path.join(output_dir, folder_name)
    else:
        full_path = folder_name
    
    os.makedirs(full_path, exist_ok=True)
    
    # Generate and write description file
    description_content = generate_description_file(config)
    with open(os.path.join(full_path, 'description.txt'), 'w') as f:
        f.write(description_content)
    
    # Generate and write test cases file
    if 'test_cases' in config:
        testcases_content = generate_testcases_file(config['test_cases'])
        with open(os.path.join(full_path, 'testcases.txt'), 'w') as f:
            f.write(testcases_content)
    
    print(f"✅ Created question files in: {full_path}/")
    print(f"   - description.txt")
    if 'test_cases' in config:
        print(f"   - testcases.txt ({len(config['test_cases'])} test cases)")
    
    return full_path

def create_sample_config():
    """Create a sample configuration file"""
    sample = {
        "title": "Sample Problem",
        "folder_name": "E1_Sample_Problem",
        "contest": "Round 1: Shattered Syntax (Debugging)",
        "problem_type": "Debugging",
        "problem_mode": "Standard Input/Output",
        "total_marks": 10,
        "constraints": "1 <= N <= 1e5",
        "description": "Given an integer N, print N.",
        "input_format": "N",
        "output_format": "N",
        "test_cases": [
            {
                "type": "Sample",
                "points": 0,
                "input": "5",
                "output": "5"
            },
            {
                "type": "Sample",
                "points": 0,
                "input": "10",
                "output": "10"
            },
            {
                "type": "Hidden",
                "points": "auto",
                "input": "100",
                "output": "100"
            }
        ]
    }
    
    with open('question_template.json', 'w') as f:
        json.dump(sample, f, indent=2)
    
    print("✅ Created sample configuration: question_template.json")
    print("\nEdit this file with your question details, then run:")
    print("  python3 create_question_from_file.py question_template.json")

def main():
    """Entry point"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 create_question_from_file.py <config.json> [output_dir]")
        print("\nOr create a sample template:")
        print("  python3 create_question_from_file.py --template")
        sys.exit(1)
    
    if sys.argv[1] == '--template':
        create_sample_config()
        sys.exit(0)
    
    config_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(config_file):
        print(f"Error: Configuration file '{config_file}' not found")
        sys.exit(1)
    
    try:
        create_question_from_config(config_file, output_dir)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
Interactive script to create question files for the coding contest platform.
Generates description.txt and testcases.txt files in the proper format.
"""

import os
import sys

def get_input(prompt, default=None, multiline=False):
    """Get input from user with optional default value"""
    if default:
        prompt = f"{prompt} [{default}]: "
    else:
        prompt = f"{prompt}: "
    
    if multiline:
        print(prompt)
        print("(Enter multiple lines, type 'END' on a new line when done)")
        lines = []
        while True:
            line = input()
            if line.strip() == 'END':
                break
            lines.append(line)
        return '\n'.join(lines)
    else:
        value = input(prompt)
        return value if value else default

def get_difficulty():
    """Get problem difficulty"""
    print("\nSelect Difficulty:")
    print("1. Easy (E)")
    print("2. Medium (M)")
    print("3. Hard (H)")
    
    while True:
        choice = input("Enter choice (1-3): ")
        if choice == '1':
            return 'E', 'Easy', 10
        elif choice == '2':
            return 'M', 'Medium', 20
        elif choice == '3':
            return 'H', 'Hard', 30
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")

def get_test_cases():
    """Collect test cases from user"""
    test_cases = []
    
    print("\n" + "="*60)
    print("TEST CASES")
    print("="*60)
    
    # Sample test cases
    num_sample = int(get_input("\nHow many SAMPLE test cases (visible to participants)", "3"))
    
    for i in range(num_sample):
        print(f"\n--- Sample Test Case {i+1} ---")
        test_input = get_input("Input", multiline=True)
        test_output = get_input("Output", multiline=True)
        
        test_cases.append({
            'number': i + 1,
            'type': 'Sample',
            'points': 0,
            'input': test_input,
            'output': test_output
        })
    
    # Hidden test cases
    num_hidden = int(get_input("\nHow many HIDDEN test cases (for evaluation)", "10"))
    
    for i in range(num_hidden):
        print(f"\n--- Hidden Test Case {i+1} ---")
        test_input = get_input("Input", multiline=True)
        test_output = get_input("Output", multiline=True)
        
        test_cases.append({
            'number': len(test_cases) + 1,
            'type': 'Hidden',
            'points': 'auto',
            'input': test_input,
            'output': test_output
        })
    
    return test_cases

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
    
    for tc in test_cases:
        lines.append(f"# Test Case {tc['number']} ({tc['type']}) - {tc['points']} points" if tc['points'] != 'auto' else f"# Test Case {tc['number']} ({tc['type']}) - will get auto points")
        lines.append("INPUT:")
        lines.append(tc['input'])
        lines.append("OUTPUT:")
        lines.append(tc['output'])
        lines.append("")  # Empty line between test cases
    
    return '\n'.join(lines)

def create_question_files(output_dir):
    """Main function to create question files"""
    print("="*60)
    print("CODING CONTEST QUESTION CREATOR")
    print("="*60)
    
    # Collect basic information
    print("\n" + "="*60)
    print("BASIC INFORMATION")
    print("="*60)
    
    title = get_input("\nProblem Title (e.g., 'Palindrome Checker')")
    
    difficulty_code, difficulty_name, default_marks = get_difficulty()
    
    problem_number = get_input(f"\nProblem Number (e.g., '1' for {difficulty_code}1)", "1")
    
    folder_name = f"{difficulty_code}{problem_number}_{title.replace(' ', '_')}"
    
    contest = get_input("\nContest Name", "Round 1: Shattered Syntax (Debugging)")
    problem_type = get_input("Problem Type", "Debugging")
    problem_mode = get_input("Problem Mode", "Standard Input/Output")
    total_marks = get_input("Total Marks", str(default_marks))
    
    # Collect problem details
    print("\n" + "="*60)
    print("PROBLEM DETAILS")
    print("="*60)
    
    print("\nConstraints (e.g., '1 <= N <= 1e5; 1 <= M <= 1e6'):")
    constraints = get_input("Constraints", multiline=True)
    
    print("\nProblem Description:")
    description = get_input("Description", multiline=True)
    
    print("\nInput Format (describe the input structure):")
    input_format = get_input("Input Format", multiline=True)
    
    print("\nOutput Format (describe the expected output):")
    output_format = get_input("Output Format", multiline=True)
    
    # Collect test cases
    test_cases = get_test_cases()
    
    # Prepare data
    data = {
        'title': title,
        'contest': contest,
        'problem_type': problem_type,
        'problem_mode': problem_mode,
        'total_marks': total_marks,
        'constraints': constraints,
        'description': description,
        'input_format': input_format,
        'output_format': output_format
    }
    
    # Generate files
    description_content = generate_description_file(data)
    testcases_content = generate_testcases_file(test_cases)
    
    # Create output directory
    if output_dir:
        full_path = os.path.join(output_dir, folder_name)
    else:
        full_path = folder_name
    
    os.makedirs(full_path, exist_ok=True)
    
    # Write files
    with open(os.path.join(full_path, 'description.txt'), 'w') as f:
        f.write(description_content)
    
    with open(os.path.join(full_path, 'testcases.txt'), 'w') as f:
        f.write(testcases_content)
    
    print("\n" + "="*60)
    print("SUCCESS!")
    print("="*60)
    print(f"\nFiles created in: {full_path}/")
    print(f"  - description.txt")
    print(f"  - testcases.txt")
    print("\nYou can now add starter code and solution files to this directory.")

def main():
    """Entry point"""
    print("\nWelcome to the Coding Contest Question Creator!\n")
    
    # Ask for output directory
    output_dir = get_input("Output directory (leave empty for current directory)", ".")
    
    try:
        create_question_files(output_dir)
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nError: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()

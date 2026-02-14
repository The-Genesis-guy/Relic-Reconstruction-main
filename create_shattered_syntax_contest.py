#!/usr/bin/env python3
"""
Create "RR - The Shattered Syntax" Contest
Import all 10 problems from round1_full_pack with proper marks distribution
"""

import sqlite3
import sys
import os
from datetime import datetime, timedelta

# Add current directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'coding-contest'))
import config

def get_db():
    """Get database connection."""
    conn = sqlite3.connect(config.DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def parse_test_cases(testcase_file):
    """Parse testcases.txt file."""
    with open(testcase_file, 'r') as f:
        content = f.read()
    
    test_cases = []
    lines = content.split('\n')
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        
        if line.startswith('#') and 'Test Case' in line:
            is_sample = 'Sample' in line or 'sample' in line
            
            # Find INPUT section
            i += 1
            while i < len(lines) and not lines[i].strip().startswith('INPUT:'):
                i += 1
            
            if i >= len(lines):
                break
            
            # Collect input
            i += 1
            input_lines = []
            while i < len(lines) and not lines[i].strip().startswith('OUTPUT:'):
                input_lines.append(lines[i])
                i += 1
            
            if i >= len(lines):
                break
            
            # Collect output
            i += 1
            output_lines = []
            while i < len(lines):
                line = lines[i].strip()
                if line.startswith('#') and 'Test Case' in line:
                    break
                output_lines.append(lines[i])
                i += 1
            
            test_input = '\n'.join(input_lines).strip()
            expected_output = '\n'.join(output_lines).strip()
            
            if test_input and expected_output:
                test_cases.append({
                    'input': test_input,
                    'expected_output': expected_output,
                    'is_sample': is_sample
                })
        else:
            i += 1
    
    return test_cases

def read_code_file(filepath):
    """Read code file content."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except:
        return ""

def create_contest(conn):
    """Create the contest."""
    # Check if contest already exists
    existing = conn.execute(
        "SELECT id FROM contests WHERE title = ?",
        ("RR - The Shattered Syntax",)
    ).fetchone()
    
    if existing:
        print(f"Contest already exists with ID: {existing['id']}")
        return existing['id']
    
    # Create contest (3 hour duration)
    now = datetime.now()
    start_time = now.strftime('%Y-%m-%d %H:%M:%S')
    end_time = (now + timedelta(hours=3)).strftime('%Y-%m-%d %H:%M:%S')
    
    cursor = conn.execute('''
        INSERT INTO contests (title, description, start_time, end_time, is_active, show_leaderboard)
        VALUES (?, ?, ?, ?, 1, 1)
    ''', (
        "RR - The Shattered Syntax",
        "A comprehensive coding challenge featuring 10 algorithmic problems across Easy, Medium, and Hard difficulties. Test your problem-solving skills with palindromes, arrays, dynamic programming, graphs, and more!",
        start_time,
        end_time
    ))
    
    contest_id = cursor.lastrowid
    conn.commit()
    print(f"✅ Created contest: RR - The Shattered Syntax (ID: {contest_id})")
    print(f"   Start: {start_time}")
    print(f"   End: {end_time}")
    return contest_id

def import_problem(conn, contest_id, problem_dir, problem_name, total_marks, difficulty, order):
    """Import a single problem."""
    print(f"\n📝 Importing: {problem_name} ({total_marks} marks, {difficulty})")
    
    # Read description
    desc_file = os.path.join(problem_dir, 'description.txt')
    with open(desc_file, 'r') as f:
        desc_content = f.read()
    
    # Parse description
    lines = desc_content.split('\n')
    title = ""
    description = ""
    input_format = ""
    output_format = ""
    constraints = ""
    
    for line in lines:
        if line.startswith('Problem Title:'):
            title = line.replace('Problem Title:', '').strip()
        elif line.startswith('Constraints:'):
            constraints = line.replace('Constraints:', '').strip()
        elif line.startswith('Description:'):
            description = line.replace('Description:', '').strip()
        elif line.startswith('Input Format:'):
            input_format = line.replace('Input Format:', '').strip()
        elif line.startswith('Output Format:'):
            output_format = line.replace('Output Format:', '').strip()
    
    if not title:
        title = problem_name.replace('_', ' ')
    
    if not description:
        description = f"Solve the {title} problem."
    
    # Read test cases
    testcase_file = os.path.join(problem_dir, 'testcases.txt')
    test_cases = parse_test_cases(testcase_file)
    
    if not test_cases:
        print(f"   ⚠️  No test cases found!")
        return None
    
    # Get sample test cases for display
    sample_tests = [tc for tc in test_cases if tc['is_sample']]
    sample_input = sample_tests[0]['input'] if sample_tests else ""
    sample_output = sample_tests[0]['expected_output'] if sample_tests else ""
    
    # Read solution and starter code
    solution_dir = os.path.join(problem_dir, 'Solution')
    if not os.path.exists(solution_dir):
        solution_dir = os.path.join(problem_dir, 'Solutions')
    
    starter_dir = os.path.join(problem_dir, 'starter_code')
    
    # Read code files
    languages = ['python', 'cpp', 'java', 'c']
    solutions = {}
    starters = {}
    
    for lang in languages:
        if lang == 'python':
            ext = '.py'
        elif lang == 'cpp':
            ext = '.cpp'
        elif lang == 'java':
            ext = '.java'
        elif lang == 'c':
            ext = '.c'
        
        # Read solution
        sol_file = os.path.join(solution_dir, f'Solution{ext}')
        if os.path.exists(sol_file):
            solutions[lang] = read_code_file(sol_file)
        
        # Read starter code
        starter_file = os.path.join(starter_dir, f'starter{ext}')
        if os.path.exists(starter_file):
            starters[lang] = read_code_file(starter_file)
    
    # Insert problem
    cursor = conn.execute('''
        INSERT INTO problems (
            title, description, input_format, output_format, constraints,
            sample_input, sample_output, test_input, expected_output,
            problem_type, total_marks, contest_id, enabled,
            problem_mode, function_name, difficulty, round_number
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?, ?, ?)
    ''', (
        title,
        description,
        input_format,
        output_format,
        constraints,
        sample_input,
        sample_output,
        sample_input,  # test_input (legacy field)
        sample_output,  # expected_output (legacy field)
        'coding',
        total_marks,
        contest_id,
        'stdin',  # problem_mode
        'solve',  # function_name
        difficulty,
        order  # round_number for ordering
    ))
    
    problem_id = cursor.lastrowid
    conn.commit()
    
    print(f"   ✅ Created problem ID: {problem_id}")
    
    # Insert multi-language code
    for lang in languages:
        if lang in solutions or lang in starters:
            conn.execute('''
                INSERT INTO problem_code (problem_id, language, solution_code, starter_code)
                VALUES (?, ?, ?, ?)
            ''', (
                problem_id,
                lang,
                solutions.get(lang, ''),
                starters.get(lang, '')
            ))
    
    conn.commit()
    print(f"   ✅ Saved code for {len(solutions)} languages")
    
    # Insert test cases with proper point distribution
    hidden_tests = [tc for tc in test_cases if not tc['is_sample']]
    num_hidden = len(hidden_tests)
    
    if num_hidden > 0:
        points_per_test = total_marks // num_hidden
        remainder = total_marks % num_hidden
    else:
        points_per_test = 0
        remainder = 0
    
    test_order = 0
    for idx, tc in enumerate(test_cases):
        is_sample = tc['is_sample']
        
        # Sample tests get 0 points, hidden tests get distributed points
        if is_sample:
            points = 0
        else:
            points = points_per_test
            # Distribute remainder to first few tests
            if remainder > 0:
                points += 1
                remainder -= 1
        
        conn.execute('''
            INSERT INTO test_cases (
                problem_id, input, expected_output, points, is_sample, test_order
            ) VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            problem_id,
            tc['input'],
            tc['expected_output'],
            points,
            1 if is_sample else 0,
            test_order
        ))
        
        test_order += 1
    
    conn.commit()
    
    sample_count = len([tc for tc in test_cases if tc['is_sample']])
    hidden_count = len([tc for tc in test_cases if not tc['is_sample']])
    
    print(f"   ✅ Imported {len(test_cases)} test cases ({sample_count} sample, {hidden_count} hidden)")
    print(f"   💰 Points: {points_per_test} per hidden test = {total_marks} total")
    
    return problem_id

def main():
    """Main import function."""
    print("=" * 80)
    print("CREATING CONTEST: RR - The Shattered Syntax")
    print("=" * 80)
    print()
    
    base_dir = 'round1_full_pack_optionA_solutions'
    
    # Problem configuration: (folder_name, marks, difficulty, order)
    problems = [
        # Easy (10 marks each) - Total: 30
        ('E1_Palindrome_Checker', 10, 'easy', 1),
        ('E2_Array_Rotation', 10, 'easy', 2),
        ('E3_Pattern_Match_Count', 10, 'easy', 3),
        
        # Medium (20 marks each) - Total: 80
        ('M1_Longest_Valid_Parentheses', 20, 'medium', 4),
        ('M2_Longest_Substring_No_Repeat', 20, 'medium', 5),
        ('M3_Coin_Change_Min_Coins', 20, 'medium', 6),
        ('M4_Merge_Intervals', 20, 'medium', 7),
        
        # Hard (30 marks each) - Total: 90
        ('H1_Graph_Connectivity_BFS', 30, 'hard', 8),
        ('H2_Minimum_Path_Sum_Grid', 30, 'hard', 9),
        ('H3_Merge_K_Sorted_Arrays', 30, 'hard', 10),
    ]
    
    # Verify total marks
    total_marks = sum(p[1] for p in problems)
    print(f"Total marks: {total_marks}")
    print(f"Problems: {len(problems)}")
    print()
    
    if total_marks != 200:
        print(f"⚠️  WARNING: Total marks is {total_marks}, expected 200!")
        return 1
    
    # Connect to database
    conn = get_db()
    
    try:
        # Create contest
        contest_id = create_contest(conn)
        
        # Import all problems
        imported = 0
        for folder_name, marks, difficulty, order in problems:
            problem_dir = os.path.join(base_dir, folder_name)
            
            if not os.path.exists(problem_dir):
                print(f"⚠️  Problem directory not found: {problem_dir}")
                continue
            
            problem_id = import_problem(conn, contest_id, problem_dir, folder_name, marks, difficulty, order)
            
            if problem_id:
                imported += 1
        
        print()
        print("=" * 80)
        print("IMPORT COMPLETE!")
        print("=" * 80)
        print(f"✅ Contest created: RR - The Shattered Syntax (ID: {contest_id})")
        print(f"✅ Problems imported: {imported}/{len(problems)}")
        print(f"✅ Total marks: {total_marks}")
        print()
        print("Breakdown:")
        print(f"  Easy (3 problems):   3 × 10 = 30 marks")
        print(f"  Medium (4 problems): 4 × 20 = 80 marks")
        print(f"  Hard (3 problems):   3 × 30 = 90 marks")
        print(f"  TOTAL:                      200 marks")
        print()
        print("🎉 Contest is ready! Access it at: http://localhost:5000/contest/{contest_id}")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        conn.close()

if __name__ == '__main__':
    sys.exit(main())

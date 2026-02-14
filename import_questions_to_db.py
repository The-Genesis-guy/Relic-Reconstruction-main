#!/usr/bin/env python3
"""
Import questions from JSON files into the coding contest database.
Maps JSON structure to database schema and handles all fields properly.
"""

import json
import sqlite3
import os
import sys
from datetime import datetime, timedelta

# Add coding-contest directory to path
sys.path.insert(0, 'coding-contest')
try:
    import config
except ImportError:
    print("Error: Could not import config from coding-contest/")
    print("Make sure you're running this from the project root")
    sys.exit(1)

def get_difficulty_from_folder(folder_name):
    """Extract difficulty from folder name (E1, M2, H3, etc.)"""
    if folder_name.startswith('E'):
        return 'easy'
    elif folder_name.startswith('M'):
        return 'medium'
    elif folder_name.startswith('H'):
        return 'hard'
    return 'easy'

def get_sample_test_cases(test_cases):
    """Get sample test cases from test_cases array"""
    samples = [tc for tc in test_cases if tc.get('type') == 'Sample']
    if not samples:
        return "", ""
    
    # Combine all sample inputs and outputs
    sample_inputs = []
    sample_outputs = []
    
    for sample in samples:
        sample_inputs.append(sample['input'])
        sample_outputs.append(sample['output'])
    
    return '\n---\n'.join(sample_inputs), '\n---\n'.join(sample_outputs)

def create_contest_if_not_exists(cursor, contest_name):
    """Create contest if it doesn't exist, return contest_id"""
    cursor.execute("SELECT id FROM contests WHERE title = ?", (contest_name,))
    result = cursor.fetchone()
    
    if result:
        return result[0]
    
    # Create new contest
    start_time = datetime.now()
    end_time = start_time + timedelta(days=7)  # 7 days duration
    
    cursor.execute("""
        INSERT INTO contests (title, description, start_time, end_time, is_active, show_leaderboard)
        VALUES (?, ?, ?, ?, 1, 1)
    """, (contest_name, f"Contest: {contest_name}", start_time, end_time))
    
    return cursor.lastrowid

def import_question(cursor, json_data, contest_id):
    """Import a single question from JSON into database"""
    
    # Extract data from JSON
    title = json_data['title']
    description = json_data.get('description', '')
    input_format = json_data.get('input_format', '')
    output_format = json_data.get('output_format', '')
    constraints = json_data.get('constraints', '')
    total_marks = int(json_data.get('total_marks', 100))
    problem_type = json_data.get('problem_type', 'Debugging')
    problem_mode = json_data.get('problem_mode', 'Standard Input/Output')
    folder_name = json_data.get('folder_name', '')
    
    # Determine difficulty
    difficulty = get_difficulty_from_folder(folder_name)
    
    # Get test cases
    test_cases = json_data.get('test_cases', [])
    
    # Get sample test cases
    sample_input, sample_output = get_sample_test_cases(test_cases)
    
    # For legacy fields (test_input, expected_output) - use first hidden test case
    hidden_tests = [tc for tc in test_cases if tc.get('type') != 'Sample']
    if hidden_tests:
        test_input = hidden_tests[0]['input']
        expected_output = hidden_tests[0]['output']
    else:
        test_input = sample_input
        expected_output = sample_output
    
    # Get solutions (prefer Python for legacy field)
    solutions = json_data.get('solutions', {})
    reference_solution = solutions.get('python', solutions.get('java', solutions.get('cpp', '')))
    
    # Get starter code (prefer Python for legacy field)
    starter_codes = json_data.get('starter_code', {})
    starter_code = starter_codes.get('python', starter_codes.get('java', starter_codes.get('cpp', '')))
    
    # Map problem_mode
    if 'Standard Input/Output' in problem_mode or 'stdin' in problem_mode.lower():
        db_problem_mode = 'stdin'
    else:
        db_problem_mode = 'function'
    
    # Insert problem
    cursor.execute("""
        INSERT INTO problems (
            title, description, input_format, output_format,
            sample_input, sample_output, test_input, expected_output,
            enabled, problem_type, contest_id, starter_code,
            problem_mode, difficulty, reference_solution, total_marks, constraints
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        title, description, input_format, output_format,
        sample_input, sample_output, test_input, expected_output,
        problem_type, contest_id, starter_code,
        db_problem_mode, difficulty, reference_solution, total_marks, constraints
    ))
    
    problem_id = cursor.lastrowid
    
    # Insert all language solutions and starter codes
    for language, solution_code in solutions.items():
        starter = starter_codes.get(language, '')
        cursor.execute("""
            INSERT OR REPLACE INTO problem_code (problem_id, language, solution_code, starter_code)
            VALUES (?, ?, ?, ?)
        """, (problem_id, language, solution_code, starter))
    
    # Insert test cases
    for idx, test_case in enumerate(test_cases):
        is_sample = 1 if test_case.get('type') == 'Sample' else 0
        points = test_case.get('points', 0)
        
        # Calculate points for auto cases
        if points == 'auto':
            hidden_count = len([tc for tc in test_cases if tc.get('type') != 'Sample'])
            if hidden_count > 0:
                points = total_marks // hidden_count
            else:
                points = 10
        
        cursor.execute("""
            INSERT INTO test_cases (
                problem_id, input, expected_output, points, is_sample, test_order
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            problem_id, test_case['input'], test_case['output'],
            points, is_sample, idx + 1
        ))
    
    return problem_id

def upsert_question(cursor, json_data, contest_id, update_existing=False):
    """
    Insert a question, or update an existing one in the same contest (matched by title).

    Update mode replaces:
      - problems row fields
      - all test_cases for the problem
      - all problem_code rows (per language) via INSERT OR REPLACE
    """
    title = json_data['title']

    existing_problem_id = None
    if update_existing:
        cursor.execute(
            "SELECT id FROM problems WHERE contest_id = ? AND title = ?",
            (contest_id, title),
        )
        row = cursor.fetchone()
        if row:
            existing_problem_id = row[0]

    if existing_problem_id is None:
        problem_id = import_question(cursor, json_data, contest_id)
        return problem_id, "inserted"

    # Recompute all fields (same logic as import_question)
    description = json_data.get('description', '')
    input_format = json_data.get('input_format', '')
    output_format = json_data.get('output_format', '')
    constraints = json_data.get('constraints', '')
    total_marks = int(json_data.get('total_marks', 100))
    problem_type = json_data.get('problem_type', 'Debugging')
    problem_mode = json_data.get('problem_mode', 'Standard Input/Output')
    folder_name = json_data.get('folder_name', '')

    difficulty = get_difficulty_from_folder(folder_name)

    test_cases = json_data.get('test_cases', [])
    sample_input, sample_output = get_sample_test_cases(test_cases)

    hidden_tests = [tc for tc in test_cases if tc.get('type') != 'Sample']
    if hidden_tests:
        test_input = hidden_tests[0]['input']
        expected_output = hidden_tests[0]['output']
    else:
        test_input = sample_input
        expected_output = sample_output

    solutions = json_data.get('solutions', {})
    reference_solution = solutions.get('python', solutions.get('java', solutions.get('cpp', '')))

    starter_codes = json_data.get('starter_code', {})
    starter_code = starter_codes.get('python', starter_codes.get('java', starter_codes.get('cpp', '')))

    if 'Standard Input/Output' in problem_mode or 'stdin' in problem_mode.lower():
        db_problem_mode = 'stdin'
    else:
        db_problem_mode = 'function'

    cursor.execute(
        """
        UPDATE problems SET
            description = ?,
            input_format = ?,
            output_format = ?,
            sample_input = ?,
            sample_output = ?,
            test_input = ?,
            expected_output = ?,
            problem_type = ?,
            starter_code = ?,
            problem_mode = ?,
            difficulty = ?,
            reference_solution = ?,
            total_marks = ?,
            constraints = ?
        WHERE id = ?
        """,
        (
            description,
            input_format,
            output_format,
            sample_input,
            sample_output,
            test_input,
            expected_output,
            problem_type,
            starter_code,
            db_problem_mode,
            difficulty,
            reference_solution,
            total_marks,
            constraints,
            existing_problem_id,
        ),
    )

    # Update per-language code
    for language, solution_code in solutions.items():
        starter = starter_codes.get(language, '')
        cursor.execute(
            """
            INSERT OR REPLACE INTO problem_code (problem_id, language, solution_code, starter_code)
            VALUES (?, ?, ?, ?)
            """,
            (existing_problem_id, language, solution_code, starter),
        )

    # Replace all test cases
    cursor.execute("DELETE FROM test_cases WHERE problem_id = ?", (existing_problem_id,))
    for idx, test_case in enumerate(test_cases):
        is_sample = 1 if test_case.get('type') == 'Sample' else 0
        points = test_case.get('points', 0)

        if points == 'auto':
            hidden_count = len([tc for tc in test_cases if tc.get('type') != 'Sample'])
            if hidden_count > 0:
                points = total_marks // hidden_count
            else:
                points = 10

        cursor.execute(
            """
            INSERT INTO test_cases (
                problem_id, input, expected_output, points, is_sample, test_order
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                existing_problem_id,
                test_case['input'],
                test_case['output'],
                points,
                is_sample,
                idx + 1,
            ),
        )

    return existing_problem_id, "updated"

def import_from_json_file(json_file, contest_name=None):
    """Import questions from a JSON file"""
    
    # Load JSON
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    # Check if it's a single question or array of questions
    if isinstance(data, list):
        questions = data
    else:
        questions = [data]
    
    # Connect to database
    db_path = config.DB_NAME
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        print("   Run: cd coding-contest && python3 init_db.py")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print(f"📁 Importing from: {json_file}")
    print(f"📊 Found {len(questions)} question(s)\n")
    
    imported = 0
    failed = 0
    
    for question in questions:
        try:
            # Determine contest name
            if contest_name:
                contest = contest_name
            else:
                contest = question.get('contest', 'Default Contest')
            
            # Create or get contest
            contest_id = create_contest_if_not_exists(cursor, contest)
            
            # Import/update question
            if globals().get("UPDATE_EXISTING", False):
                problem_id, action = upsert_question(cursor, question, contest_id, update_existing=True)
            else:
                problem_id = import_question(cursor, question, contest_id)
                action = "inserted"
            
            title = question['title']
            test_count = len(question.get('test_cases', []))
            solution_count = len(question.get('solutions', {}))
            
            print(f"✅ {title}")
            print(f"   → Problem ID: {problem_id}")
            print(f"   → Action: {action}")
            print(f"   → Contest: {contest}")
            print(f"   → Test cases: {test_count}")
            print(f"   → Difficulty: {get_difficulty_from_folder(question.get('folder_name', ''))}")
            if solution_count > 0:
                langs = ', '.join(question.get('solutions', {}).keys())
                print(f"   → Solutions: {solution_count} languages ({langs})")
            print()
            
            imported += 1
            
        except Exception as e:
            print(f"❌ Failed to import {question.get('title', 'Unknown')}: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    # Commit changes
    conn.commit()
    conn.close()
    
    print("=" * 60)
    print(f"✅ Successfully imported: {imported}")
    if failed > 0:
        print(f"❌ Failed: {failed}")
    print("=" * 60)

def import_from_directory(directory, contest_name=None):
    """Import all JSON files from a directory"""
    
    json_files = []
    for filename in sorted(os.listdir(directory)):
        if filename.endswith('.json') and filename != 'all_questions.json':
            json_files.append(os.path.join(directory, filename))
    
    if not json_files:
        print(f"❌ No JSON files found in {directory}")
        return
    
    print(f"📁 Found {len(json_files)} JSON file(s) in {directory}\n")
    
    for json_file in json_files:
        import_from_json_file(json_file, contest_name)
        print()

def main():
    """Entry point"""
    global UPDATE_EXISTING
    UPDATE_EXISTING = False

    argv = sys.argv[1:]
    if '--update' in argv:
        UPDATE_EXISTING = True
        argv.remove('--update')

    if len(argv) < 1:
        print("Import Questions to Database")
        print("=" * 60)
        print("\nUsage:")
        print("  python3 import_questions_to_db.py [--update] <json_file_or_directory> [contest_name]")
        print("\nExamples:")
        print("  # Import single question")
        print("  python3 import_questions_to_db.py question.json")
        print()
        print("  # Update existing questions (match by title within contest)")
        print("  python3 import_questions_to_db.py --update round1_full_pack_optionA_solutions/json_output/ \"Round 1: Shattered Syntax (Debugging)\"")
        print()
        print("  # Import all questions from directory")
        print("  python3 import_questions_to_db.py round1_full_pack_optionA_solutions/json_output/")
        print()
        print("  # Import with custom contest name")
        print("  python3 import_questions_to_db.py questions/ \"Round 1: Finals\"")
        print()
        sys.exit(1)
    
    path = argv[0]
    contest_name = argv[1] if len(argv) > 1 else None
    
    if not os.path.exists(path):
        print(f"❌ Error: Path not found: {path}")
        sys.exit(1)
    
    try:
        if os.path.isdir(path):
            import_from_directory(path, contest_name)
        else:
            import_from_json_file(path, contest_name)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()

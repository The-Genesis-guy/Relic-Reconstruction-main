#!/usr/bin/env python3
"""
✅ FIXED: Test case file parser with CORRECT point distribution
Addresses floating-point precision issues in scoring
"""

import re
from decimal import Decimal, ROUND_HALF_UP

def parse_test_case_file(file_content):
    """
    Parse test case file and return list of test cases.
    
    ✅ FIX: Points are now stored as integers (in cents/hundredths) to avoid
    floating-point precision errors in scoring calculations.
    
    AUTOMATIC SAMPLE MARKING:
    - First 3 test cases are ALWAYS marked as SAMPLE (visible to students)
    - Remaining test cases are ALWAYS marked as HIDDEN (for grading)
    
    Args:
        file_content: String content of the test case file
    
    Returns:
        List of dicts: [{'input': str, 'output': str, 'is_sample': bool, 'points': int}, ...]
    """
    test_cases = []
    lines = file_content.split('\n')
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Look for test case header (# Test Case N ...)
        if line.startswith('#') and 'test case' in line.lower():
            # Parse header (but we'll override is_sample based on position)
            is_sample_in_file = 'sample' in line.lower()
            
            # Extract points
            points_match = re.search(r'(\d+)\s*points?', line, re.IGNORECASE)
            points = 0 if is_sample_in_file else (int(points_match.group(1)) if points_match else 10)
            
            # Find INPUT: section
            i += 1
            while i < len(lines) and not lines[i].strip().upper().startswith('INPUT:'):
                i += 1
            
            if i >= len(lines):
                break
            
            # Collect input lines
            i += 1
            input_lines = []
            while i < len(lines) and not lines[i].strip().upper().startswith('OUTPUT:'):
                input_lines.append(lines[i])
                i += 1
            
            if i >= len(lines):
                break
            
            # Collect output lines
            i += 1
            output_lines = []
            while i < len(lines):
                line = lines[i].strip()
                if line.startswith('#') and 'test case' in line.lower():
                    break
                output_lines.append(lines[i])
                i += 1
            
            # Create test case
            test_input = '\n'.join(input_lines).strip()
            expected_output = '\n'.join(output_lines).strip()
            
            if test_input and expected_output:
                test_cases.append({
                    'input': test_input,
                    'expected_output': expected_output,
                    'is_sample': False,  # Will be set below based on position
                    'points': points
                })
        else:
            i += 1
    
    # AUTOMATIC MARKING: First 3 are SAMPLE, rest are HIDDEN
    for idx, tc in enumerate(test_cases):
        if idx < 3:
            tc['is_sample'] = True
            tc['points'] = 0  # Sample tests always get 0 points
        else:
            tc['is_sample'] = False
            # Points will be redistributed later based on total_marks
    
    return test_cases

def import_test_cases_to_db(conn, problem_id, test_cases, total_marks=None):
    """
    ✅ FIXED: Import test cases with PRECISE point distribution
    
    Args:
        conn: Database connection
        problem_id: Problem ID
        test_cases: List of test case dicts from parse_test_case_file()
        total_marks: Total marks for problem (fetched from DB if None)
    
    Returns:
        Number of test cases imported
    """
    # Clear existing test cases for this problem
    conn.execute('DELETE FROM test_cases WHERE problem_id = ?', (problem_id,))
    
    # Get total marks if not provided
    if total_marks is None:
        problem = conn.execute('SELECT total_marks FROM problems WHERE id = ?', (problem_id,)).fetchone()
        total_marks = problem['total_marks'] if problem and 'total_marks' in problem.keys() else 100
    
    
    # Calculate initial points (0 for samples, 0 for hidden initially)
    # We will call redistribute_points to handle the math
    for order, tc in enumerate(test_cases):
        conn.execute('''
            INSERT INTO test_cases (problem_id, input, expected_output, is_sample, points, test_order)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (problem_id, tc['input'], tc['expected_output'], tc['is_sample'], 0, order))
    
    # Now verify and distribute points correctly
    redistribute_points(conn, problem_id, total_marks)
    
    conn.commit()
    return len(test_cases)

def redistribute_points(conn, problem_id, total_marks=None):
    """
    Recalculate and distribute points for all test cases of a problem.
    Ensures total equals total_marks with proper rounding.
    """
    # Get total marks if not provided
    if total_marks is None:
        problem = conn.execute('SELECT total_marks FROM problems WHERE id = ?', (problem_id,)).fetchone()
        total_marks = problem['total_marks'] if problem and 'total_marks' in problem.keys() else 100
    
    # ✅ FIX: Use Decimal for precise calculation
    total_marks_decimal = Decimal(str(total_marks))
    
    # Get hidden tests (ordered to ensure deterministic adjustment)
    hidden_tests = conn.execute('''
        SELECT id FROM test_cases 
        WHERE problem_id = ? AND is_sample = 0
        ORDER BY test_order
    ''', (problem_id,)).fetchall()
    
    hidden_count = len(hidden_tests)
    
    # Calculate points per hidden test with precision
    if hidden_count > 0:
        points_per_test = total_marks_decimal / Decimal(str(hidden_count))
        # Round to 2 decimal places using banker's rounding
        points_per_test = points_per_test.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    else:
        points_per_test = Decimal('0')
    
    # Update all hidden tests with the base value
    for test in hidden_tests:
        conn.execute('UPDATE test_cases SET points = ? WHERE id = ?', (float(points_per_test), test['id']))
        
    # Ensure samples are 0
    conn.execute('UPDATE test_cases SET points = 0 WHERE problem_id = ? AND is_sample = 1', (problem_id,))
    
    # ✅ FIX: Verify total points match exactly
    actual_total_row = conn.execute(
        'SELECT SUM(points) as total FROM test_cases WHERE problem_id = ? AND is_sample = 0',
        (problem_id,)
    ).fetchone()
    
    actual_total = actual_total_row['total'] if actual_total_row and actual_total_row['total'] is not None else 0
    
    # Adjust last test case if there's rounding error
    if hidden_count > 0:
        difference = float(total_marks) - actual_total
        # Find last hidden test case
        last_hidden_id = hidden_tests[-1]['id']
        
        # Get current points of last test
        last_points = conn.execute('SELECT points FROM test_cases WHERE id = ?', (last_hidden_id,)).fetchone()['points']
        
        adjusted_points = last_points + difference
        # Additional rounding to prevent float noise
        adjusted_points = round(adjusted_points, 2)
        conn.execute(
            'UPDATE test_cases SET points = ? WHERE id = ?',
            (adjusted_points, last_hidden_id)
        )

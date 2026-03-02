#!/usr/bin/env python3
"""
Multi-test case judging wrapper.
Runs code against multiple test cases and aggregates results.
"""

import config
from src.judge import judge_submission

def judge_multiple_tests(language, code, test_cases, mode='stdin', function_name='solve'):
    """
    Run code against multiple test cases.
    
    Args:
        language: Programming language
        code: Source code
        test_cases: List of dicts with 'input', 'expected_output', 'is_sample', 'points'
    
    Returns:
        dict: {
            'verdict': 'AC'|'WA'|'CE'|'RE'|'TLE',
            'total_passed': int,
            'total_tests': int,
            'test_results': [{'test_num': int, 'verdict': str, 'output': str, 'is_sample': bool}],
            'message': str,
            'points': int,
            'max_points': int
        }
    """
    if not test_cases:
        return {
            'verdict': 'CE',
            'total_passed': 0,
            'total_tests': 0,
            'test_results': [],
            'message': 'No test cases found',
            'points': 0,
            'max_points': 0
        }
    
    test_results = []
    total_passed = 0
    total_points = 0
    # max_points should only include points from hidden tests if samples are marked 0 points
    # or include everything if that's how the problem is set up.
    # To be safe, we sum what the student CAN actually earn.
    max_points = sum(tc.get('points', 0) for tc in test_cases if not tc.get('is_sample', False))
    # If no hidden tests have points, fall back to total points
    if max_points == 0:
        max_points = sum(tc.get('points', 0) for tc in test_cases)
        
    first_error_verdict = None
    
    for idx, test_case in enumerate(test_cases, 1):
        test_input = test_case['input']
        expected_output = test_case['expected_output']
        is_sample = test_case.get('is_sample', False)
        points = test_case.get('points', 0)
        
        # Run the test
        verdict, actual_output = judge_submission(
            language, code, test_input, expected_output, mode=mode, function_name=function_name
        )
        
        assigned_points = points if verdict == 'AC' else 0
        
        test_results.append({
            'test_num': idx,
            'verdict': verdict,
            'output': actual_output,
            'is_sample': is_sample,
            'points': assigned_points
        })
        
        if verdict == 'AC':
            total_passed += 1
            # Points are generally only recorded for the leaderboard from hidden tests
            # unless the contest specifically gives points for samples.
            if not is_sample:
                total_points += points
            elif max_points == sum(tc.get('points', 0) for tc in test_cases):
                # If we included samples in max_points, award them here too
                total_points += points
        elif first_error_verdict is None:
            first_error_verdict = verdict
        
    # Determine overall verdict
    if total_passed == len(test_cases):
        overall_verdict = 'AC'
        message = f'All tests passed! ({total_passed}/{len(test_cases)})'
    elif total_passed > 0:
        # Partial credit: some tests passed
        if first_error_verdict in ['CE', 'RE', 'TLE']:
            overall_verdict = first_error_verdict
            message = f'{first_error_verdict} on test {len(test_results)} (passed {total_passed} tests)'
        else:
            overall_verdict = 'PC'
            message = f'Partial Credit: {total_passed}/{len(test_cases)} tests passed'
    elif first_error_verdict:
        overall_verdict = first_error_verdict
        message = f'{first_error_verdict} on test {len(test_results)}'
    else:
        overall_verdict = 'WA'
        message = f'Wrong Answer: 0/{len(test_cases)} tests passed'
    
    return {
        'verdict': overall_verdict,
        'total_passed': total_passed,
        'total_tests': len(test_cases),
        'test_results': test_results,
        'message': message,
        'points': total_points,
        'max_points': max_points
    }


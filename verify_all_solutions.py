#!/usr/bin/env python3
"""
Verify all solutions in round1_full_pack match their test cases
"""

import subprocess
import os
import sys

def parse_test_cases(testcase_file):
    """Parse testcases.txt file and extract test cases."""
    with open(testcase_file, 'r') as f:
        content = f.read()
    
    test_cases = []
    lines = content.split('\n')
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        
        # Look for test case header
        if line.startswith('#') and 'Test Case' in line:
            # Extract input
            i += 1
            while i < len(lines) and not lines[i].strip().startswith('INPUT:'):
                i += 1
            
            if i >= len(lines):
                break
            
            # Collect input lines
            i += 1
            input_lines = []
            while i < len(lines) and not lines[i].strip().startswith('OUTPUT:'):
                input_lines.append(lines[i])
                i += 1
            
            if i >= len(lines):
                break
            
            # Collect output lines
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
                    'expected': expected_output
                })
        else:
            i += 1
    
    return test_cases

def test_solution(solution_path, test_input):
    """Run solution with test input and return output."""
    try:
        result = subprocess.run(
            ['python3', solution_path],
            input=test_input,
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.stdout.strip(), result.returncode
    except subprocess.TimeoutExpired:
        return None, -1
    except Exception as e:
        return str(e), -1

def main():
    base_dir = 'round1_full_pack_optionA_solutions'
    
    # Find all problem directories
    problems = []
    for item in os.listdir(base_dir):
        item_path = os.path.join(base_dir, item)
        if os.path.isdir(item_path) and item != 'json_output':
            problems.append(item)
    
    problems.sort()
    
    total_problems = 0
    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    
    print("=" * 80)
    print("VERIFYING ALL SOLUTIONS IN round1_full_pack")
    print("=" * 80)
    print()
    
    for problem in problems:
        problem_dir = os.path.join(base_dir, problem)
        testcase_file = os.path.join(problem_dir, 'testcases.txt')
        
        # Find solution file (could be in Solution/ or Solutions/)
        solution_file = None
        for subdir in ['Solution', 'Solutions']:
            candidate = os.path.join(problem_dir, subdir, 'Solution.py')
            if os.path.exists(candidate):
                solution_file = candidate
                break
        
        if not solution_file or not os.path.exists(testcase_file):
            print(f"⚠️  {problem}: Missing files")
            continue
        
        # Parse test cases
        test_cases = parse_test_cases(testcase_file)
        
        if not test_cases:
            print(f"⚠️  {problem}: No test cases found")
            continue
        
        total_problems += 1
        problem_passed = 0
        problem_failed = 0
        
        print(f"📝 {problem}")
        print(f"   Solution: {solution_file}")
        print(f"   Test cases: {len(test_cases)}")
        
        for idx, test_case in enumerate(test_cases, 1):
            total_tests += 1
            output, returncode = test_solution(solution_file, test_case['input'])
            
            if returncode != 0:
                print(f"   ❌ Test {idx}: Runtime Error (exit code {returncode})")
                failed_tests += 1
                problem_failed += 1
                continue
            
            if output == test_case['expected']:
                print(f"   ✅ Test {idx}: PASS")
                passed_tests += 1
                problem_passed += 1
            else:
                print(f"   ❌ Test {idx}: FAIL")
                print(f"      Expected: {test_case['expected'][:50]}...")
                print(f"      Got:      {output[:50]}...")
                failed_tests += 1
                problem_failed += 1
        
        if problem_failed == 0:
            print(f"   ✅ ALL {problem_passed} TESTS PASSED")
        else:
            print(f"   ⚠️  {problem_passed} passed, {problem_failed} failed")
        print()
    
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Problems tested: {total_problems}")
    print(f"Total tests: {total_tests}")
    print(f"✅ Passed: {passed_tests} ({passed_tests*100//total_tests if total_tests > 0 else 0}%)")
    print(f"❌ Failed: {failed_tests} ({failed_tests*100//total_tests if total_tests > 0 else 0}%)")
    print()
    
    if failed_tests == 0:
        print("🎉 ALL SOLUTIONS ARE CORRECT!")
        return 0
    else:
        print("⚠️  SOME SOLUTIONS HAVE ISSUES")
        return 1

if __name__ == '__main__':
    sys.exit(main())

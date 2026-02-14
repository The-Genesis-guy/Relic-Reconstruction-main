"""
PROBLEM: Advanced Binary Search with Statistics

Implement binary search that not only finds an element but also tracks:
- Number of comparisons made
- Middle indices calculated during search
- Whether element was found

The algorithm should work correctly for very large arrays.

INPUT: Sorted array and target value to search
OUTPUT: Index of target (or -1), number of comparisons, search path

EXPECTED BEHAVIOR:
Array: [1, 3, 5, 7, 9, 11, 13, 15, 17, 19]
Search for 13:
  - Found at index 6
  - Comparisons: 3-4
  - Path: mid=4(9), mid=7(15), mid=5(11), mid=6(13) ✓

BUG: The code fails on very large arrays or produces infinite loops.
     Find and fix the subtle bug!
"""

import sys

class SearchResult:
    def __init__(self):
        self.index = -1
        self.comparisons = 0
        self.midIndices = []

def binarySearch(arr, target):
    result = SearchResult()
    left = 0
    right = len(arr) - 1
    
    # Simulate 32-bit integer limit for consistency with other languages
    INT_MAX = 2**31 - 1
    
    while left <= right:
        # BUG HERE: Integer overflow when left and right are large
        # In Python, integers can be arbitrarily large, but we simulate 32-bit overflow
        mid_calc = left + right
        
        # Simulate overflow behavior
        if mid_calc > INT_MAX:
            # Simulating 32-bit overflow wrapping
            mid_calc = mid_calc % (2 * INT_MAX + 2)
            if mid_calc > INT_MAX:
                mid_calc = mid_calc - 2 * INT_MAX - 2
        
        mid = mid_calc // 2  # BUG: Should be left + (right - left) // 2
        
        result.midIndices.append(mid)
        result.comparisons += 1
        
        print(f"Checking index {mid} (value: {arr[mid]})")
        
        if arr[mid] == target:
            result.index = mid
            print(f"Found target at index {mid}")
            return result
        elif arr[mid] < target:
            left = mid + 1
            print(f"Target is in right half, new left: {left}")
        else:
            right = mid - 1
            print(f"Target is in left half, new right: {right}")
    
    print("Target not found in array")
    return result

def main():
    n = int(input("Enter number of elements:\n"))
    
    arr = []
    print(f"Enter {n} sorted elements:")
    for i in range(n):
        arr.append(int(input()))
    
    target = int(input("Enter target value to search:\n"))
    
    print("\n=== Binary Search Execution ===")
    result = binarySearch(arr, target)
    
    print("\n=== Search Results ===")
    if result.index != -1:
        print(f"Target found at index: {result.index}")
    else:
        print("Target not found")
    print(f"Number of comparisons: {result.comparisons}")
    print(f"Middle indices checked: {result.midIndices}")
    
    # Test with large values to demonstrate overflow
    print("\n=== Testing with large array simulation ===")
    print("For array size 2 billion, demonstrating overflow:")
    INT_MAX = 2**31 - 1
    fakeLarge = INT_MAX - 10
    fakeRight = INT_MAX - 5
    print(f"left = {fakeLarge}, right = {fakeRight}")
    
    # Simulate 32-bit overflow
    overflow_sum = fakeLarge + fakeRight
    if overflow_sum > INT_MAX:
        overflow_result = overflow_sum % (2 * INT_MAX + 2)
        if overflow_result > INT_MAX:
            overflow_result = overflow_result - 2 * INT_MAX - 2
    else:
        overflow_result = overflow_sum
    
    print(f"(left + right) / 2 = {overflow_result // 2}")
    print("This overflows to: negative number!")
    print(f"Correct: left + (right - left) / 2 = {fakeLarge + (fakeRight - fakeLarge) // 2}")

if __name__ == "__main__":
    main()

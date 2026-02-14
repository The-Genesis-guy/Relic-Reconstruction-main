"""
PROBLEM: Array Sum Calculator

Calculate the sum of all elements in an array and find the average.
The program should handle arrays of any size and return both sum and average.

INPUT: Array of integers
OUTPUT: Sum and Average of array elements

EXPECTED BEHAVIOR:
arr = [1, 2, 3, 4, 5] -> Sum: 15, Average: 3.0
arr = [10, 20, 30] -> Sum: 60, Average: 20.0
arr = [7] -> Sum: 7, Average: 7.0

BUG: The code crashes with certain inputs. Find and fix the bug!
"""

def calculateStats(arr):
    sum_val = 0
    n = len(arr)
    
    # Calculate sum using a loop
    # We iterate through all indices including the last one
    for i in range(0, n + 1):  # BUG HERE: Should be range(0, n) or range(n), not n + 1
        sum_val += arr[i]
    
    average = sum_val / n
    
    print(f"Sum: {sum_val}")
    print(f"Average: {average}")

def main():
    n = int(input("Enter number of elements:\n"))
    
    arr = []
    print(f"Enter {n} elements:")
    for i in range(n):
        arr.append(int(input()))
    
    calculateStats(arr)

if __name__ == "__main__":
    main()

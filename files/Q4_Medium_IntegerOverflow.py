"""
PROBLEM: Factorial Calculator with Validation

Calculate factorial of a number and validate if it's within safe range.
The program should handle edge cases and prevent overflow.

For reference:
5! = 120
10! = 3,628,800
15! = 1,307,674,368,000
20! = 2,432,902,008,176,640,000

INPUT: Integer n (0 <= n <= 20)
OUTPUT: Factorial of n or error message if overflow

EXPECTED BEHAVIOR:
factorial(5) -> 120
factorial(10) -> 3628800
factorial(15) -> Should show correct value
factorial(20) -> Should handle correctly or show overflow warning

BUG: The code produces incorrect results for larger numbers. Find and fix the bug!
"""

def calculateFactorial(n):
    if n < 0:
        print("Error: Negative number")
        return -1
    
    if n == 0 or n == 1:
        return 1
    
    # Simulating 32-bit integer limit for consistency with other languages
    MAX_INT = 2147483647  # 2^31 - 1
    result = 1
    
    # Calculate factorial iteratively
    for i in range(2, n + 1):
        result = result * i
        # BUG HERE: Not checking for overflow within the limit
        # In Python, integers can be arbitrarily large, but we simulate overflow
        if result > MAX_INT:
            # This wraps around like in C/Java to simulate overflow behavior
            result = result % (2 * MAX_INT + 2)  # Simulate 32-bit overflow
            if result > MAX_INT:
                result = result - 2 * MAX_INT - 2
    
    return result

def main():
    n = int(input("Enter a number (0-20):\n"))
    
    factorial = calculateFactorial(n)
    
    if factorial != -1:
        print(f"{n}! = {factorial}")
        
        # Show in scientific notation for large numbers
        if n > 15:
            print(f"Scientific notation: {factorial:.2e}")

if __name__ == "__main__":
    main()

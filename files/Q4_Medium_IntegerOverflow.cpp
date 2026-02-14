/**
 * PROBLEM: Factorial Calculator with Validation
 * 
 * Calculate factorial of a number and validate if it's within safe range.
 * The program should handle edge cases and prevent overflow.
 * 
 * For reference:
 * 5! = 120
 * 10! = 3,628,800
 * 15! = 1,307,674,368,000
 * 20! = 2,432,902,008,176,640,000
 * 
 * INPUT: Integer n (0 <= n <= 20)
 * OUTPUT: Factorial of n or error message if overflow
 * 
 * EXPECTED BEHAVIOR:
 * factorial(5) -> 120
 * factorial(10) -> 3628800
 * factorial(15) -> Should show correct value
 * factorial(20) -> Should handle correctly or show overflow warning
 * 
 * BUG: The code produces incorrect results for larger numbers. Find and fix the bug!
 */

#include <iostream>
#include <iomanip>
using namespace std;

long long calculateFactorial(int n) {
    if (n < 0) {
        cout << "Error: Negative number" << endl;
        return -1;
    }
    
    if (n == 0 || n == 1) {
        return 1;
    }
    
    int result = 1;  // BUG HERE: Using int instead of long long, causes overflow
    
    // Calculate factorial iteratively
    for (int i = 2; i <= n; i++) {
        result = result * i;  // Overflow happens here for large n
    }
    
    return result;
}

int main() {
    int n;
    
    cout << "Enter a number (0-20):" << endl;
    cin >> n;
    
    long long factorial = calculateFactorial(n);
    
    if (factorial != -1) {
        cout << n << "! = " << factorial << endl;
        
        // Show in scientific notation for large numbers
        if (n > 15) {
            cout << "Scientific notation: " << scientific << setprecision(2) 
                 << (double)factorial << endl;
        }
    }
    
    return 0;
}

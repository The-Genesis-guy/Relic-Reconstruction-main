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

import java.util.*;

public class Q4_Medium_IntegerOverflow {
    
    public static long calculateFactorial(int n) {
        if (n < 0) {
            System.out.println("Error: Negative number");
            return -1;
        }
        
        if (n == 0 || n == 1) {
            return 1;
        }
        
        int result = 1;  // BUG HERE: Using int instead of long, causes overflow
        
        // Calculate factorial iteratively
        for (int i = 2; i <= n; i++) {
            result = result * i;  // Overflow happens here for large n
        }
        
        return result;
    }
    
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        
        System.out.println("Enter a number (0-20):");
        int n = sc.nextInt();
        
        long factorial = calculateFactorial(n);
        
        if (factorial != -1) {
            System.out.println(n + "! = " + factorial);
            
            // Show in scientific notation for large numbers
            if (n > 15) {
                System.out.println("Scientific notation: " + String.format("%.2e", (double)factorial));
            }
        }
        
        sc.close();
    }
}

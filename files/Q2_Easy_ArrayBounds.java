/**
 * PROBLEM: Array Sum Calculator
 * 
 * Calculate the sum of all elements in an array and find the average.
 * The program should handle arrays of any size and return both sum and average.
 * 
 * INPUT: Array of integers
 * OUTPUT: Sum and Average of array elements
 * 
 * EXPECTED BEHAVIOR:
 * arr = [1, 2, 3, 4, 5] -> Sum: 15, Average: 3.0
 * arr = [10, 20, 30] -> Sum: 60, Average: 20.0
 * arr = [7] -> Sum: 7, Average: 7.0
 * 
 * BUG: The code crashes with certain inputs. Find and fix the bug!
 */

import java.util.*;

public class Q2_Easy_ArrayBounds {
    
    public static void calculateStats(int[] arr) {
        int sum = 0;
        int n = arr.length;
        
        // Calculate sum using a loop
        // We iterate through all indices including the last one
        for (int i = 0; i <= n; i++) {  // BUG HERE: Should be i < n, not i <= n
            sum += arr[i];
        }
        
        double average = (double) sum / n;
        
        System.out.println("Sum: " + sum);
        System.out.println("Average: " + average);
    }
    
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        
        System.out.println("Enter number of elements:");
        int n = sc.nextInt();
        
        int[] arr = new int[n];
        System.out.println("Enter " + n + " elements:");
        for (int i = 0; i < n; i++) {
            arr[i] = sc.nextInt();
        }
        
        calculateStats(arr);
        
        sc.close();
    }
}

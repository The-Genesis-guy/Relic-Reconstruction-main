/**
 * PROBLEM: Advanced Binary Search with Statistics
 * 
 * Implement binary search that not only finds an element but also tracks:
 * - Number of comparisons made
 * - Middle indices calculated during search
 * - Whether element was found
 * 
 * The algorithm should work correctly for very large arrays.
 * 
 * INPUT: Sorted array and target value to search
 * OUTPUT: Index of target (or -1), number of comparisons, search path
 * 
 * EXPECTED BEHAVIOR:
 * Array: [1, 3, 5, 7, 9, 11, 13, 15, 17, 19]
 * Search for 13:
 *   - Found at index 6
 *   - Comparisons: 3-4
 *   - Path: mid=4(9), mid=7(15), mid=5(11), mid=6(13) ✓
 * 
 * BUG: The code fails on very large arrays or produces infinite loops.
 *      Find and fix the subtle bug!
 */

import java.util.*;

public class Q9_Hard_BinarySearchBug {
    
    static class SearchResult {
        int index;
        int comparisons;
        List<Integer> midIndices;
        
        SearchResult() {
            this.index = -1;
            this.comparisons = 0;
            this.midIndices = new ArrayList<>();
        }
    }
    
    public static SearchResult binarySearch(int[] arr, int target) {
        SearchResult result = new SearchResult();
        int left = 0;
        int right = arr.length - 1;
        
        while (left <= right) {
            // BUG HERE: Integer overflow when left and right are large
            // For very large arrays, (left + right) can exceed Integer.MAX_VALUE
            int mid = (left + right) / 2;  // BUG: Should be left + (right - left) / 2
            
            result.midIndices.add(mid);
            result.comparisons++;
            
            System.out.println("Checking index " + mid + " (value: " + arr[mid] + ")");
            
            if (arr[mid] == target) {
                result.index = mid;
                System.out.println("Found target at index " + mid);
                return result;
            } else if (arr[mid] < target) {
                left = mid + 1;
                System.out.println("Target is in right half, new left: " + left);
            } else {
                right = mid - 1;
                System.out.println("Target is in left half, new right: " + right);
            }
        }
        
        System.out.println("Target not found in array");
        return result;
    }
    
    // Additional potential bug: infinite loop with incorrect boundary updates
    public static int buggyBinarySearch(int[] arr, int target) {
        int left = 0;
        int right = arr.length - 1;
        
        while (left < right) {  // Note: < instead of <=
            int mid = (left + right) / 2;
            
            if (arr[mid] == target) {
                return mid;
            } else if (arr[mid] < target) {
                left = mid;  // BUG: Should be mid + 1, can cause infinite loop
            } else {
                right = mid - 1;
            }
        }
        
        return -1;
    }
    
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        
        System.out.println("Enter number of elements:");
        int n = sc.nextInt();
        
        int[] arr = new int[n];
        System.out.println("Enter " + n + " sorted elements:");
        for (int i = 0; i < n; i++) {
            arr[i] = sc.nextInt();
        }
        
        System.out.println("Enter target value to search:");
        int target = sc.nextInt();
        
        System.out.println("\n=== Binary Search Execution ===");
        SearchResult result = binarySearch(arr, target);
        
        System.out.println("\n=== Search Results ===");
        if (result.index != -1) {
            System.out.println("Target found at index: " + result.index);
        } else {
            System.out.println("Target not found");
        }
        System.out.println("Number of comparisons: " + result.comparisons);
        System.out.println("Middle indices checked: " + result.midIndices);
        
        // Test with large values to demonstrate overflow
        System.out.println("\n=== Testing with large array simulation ===");
        System.out.println("For array size 2 billion, demonstrating overflow:");
        int fakeLarge = Integer.MAX_VALUE - 10;
        int fakeRight = Integer.MAX_VALUE - 5;
        System.out.println("left = " + fakeLarge + ", right = " + fakeRight);
        System.out.println("(left + right) / 2 = " + ((fakeLarge + fakeRight) / 2));
        System.out.println("This overflows to: negative number!");
        System.out.println("Correct: left + (right - left) / 2 = " + 
                         (fakeLarge + (fakeRight - fakeLarge) / 2));
        
        sc.close();
    }
}

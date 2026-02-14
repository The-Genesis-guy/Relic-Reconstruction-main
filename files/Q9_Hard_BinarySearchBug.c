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

#include <stdio.h>
#include <stdlib.h>
#include <limits.h>

typedef struct {
    int index;
    int comparisons;
    int* midIndices;
    int midCount;
} SearchResult;

SearchResult binarySearch(int arr[], int n, int target) {
    SearchResult result;
    result.index = -1;
    result.comparisons = 0;
    result.midIndices = (int*)malloc(32 * sizeof(int));  // Max 32 levels for binary search
    result.midCount = 0;
    
    int left = 0;
    int right = n - 1;
    
    while (left <= right) {
        // BUG HERE: Integer overflow when left and right are large
        // For very large arrays, (left + right) can exceed INT_MAX
        int mid = (left + right) / 2;  // BUG: Should be left + (right - left) / 2
        
        result.midIndices[result.midCount++] = mid;
        result.comparisons++;
        
        printf("Checking index %d (value: %d)\n", mid, arr[mid]);
        
        if (arr[mid] == target) {
            result.index = mid;
            printf("Found target at index %d\n", mid);
            return result;
        } else if (arr[mid] < target) {
            left = mid + 1;
            printf("Target is in right half, new left: %d\n", left);
        } else {
            right = mid - 1;
            printf("Target is in left half, new right: %d\n", right);
        }
    }
    
    printf("Target not found in array\n");
    return result;
}

int main() {
    int n;
    
    printf("Enter number of elements:\n");
    scanf("%d", &n);
    
    int* arr = (int*)malloc(n * sizeof(int));
    
    printf("Enter %d sorted elements:\n", n);
    for (int i = 0; i < n; i++) {
        scanf("%d", &arr[i]);
    }
    
    int target;
    printf("Enter target value to search:\n");
    scanf("%d", &target);
    
    printf("\n=== Binary Search Execution ===\n");
    SearchResult result = binarySearch(arr, n, target);
    
    printf("\n=== Search Results ===\n");
    if (result.index != -1) {
        printf("Target found at index: %d\n", result.index);
    } else {
        printf("Target not found\n");
    }
    printf("Number of comparisons: %d\n", result.comparisons);
    printf("Middle indices checked: ");
    for (int i = 0; i < result.midCount; i++) {
        printf("%d ", result.midIndices[i]);
    }
    printf("\n");
    
    // Test with large values to demonstrate overflow
    printf("\n=== Testing with large array simulation ===\n");
    printf("For array size 2 billion, demonstrating overflow:\n");
    int fakeLarge = INT_MAX - 10;
    int fakeRight = INT_MAX - 5;
    printf("left = %d, right = %d\n", fakeLarge, fakeRight);
    printf("(left + right) / 2 = %d\n", (fakeLarge + fakeRight) / 2);
    printf("This overflows to: negative number!\n");
    printf("Correct: left + (right - left) / 2 = %d\n", 
           fakeLarge + (fakeRight - fakeLarge) / 2);
    
    free(arr);
    free(result.midIndices);
    
    return 0;
}

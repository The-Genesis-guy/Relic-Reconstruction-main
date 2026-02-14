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

#include <stdio.h>
#include <stdlib.h>

void calculateStats(int arr[], int n) {
    int sum = 0;
    
    // Calculate sum using a loop
    // We iterate through all indices including the last one
    for (int i = 0; i <= n; i++) {  // BUG HERE: Should be i < n, not i <= n
        sum += arr[i];
    }
    
    double average = (double) sum / n;
    
    printf("Sum: %d\n", sum);
    printf("Average: %.2f\n", average);
}

int main() {
    int n;
    
    printf("Enter number of elements:\n");
    scanf("%d", &n);
    
    int* arr = (int*)malloc(n * sizeof(int));
    
    printf("Enter %d elements:\n", n);
    for (int i = 0; i < n; i++) {
        scanf("%d", &arr[i]);
    }
    
    calculateStats(arr, n);
    
    free(arr);
    return 0;
}

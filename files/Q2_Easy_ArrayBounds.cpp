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

#include <iostream>
#include <vector>
using namespace std;

void calculateStats(vector<int>& arr) {
    int sum = 0;
    int n = arr.size();
    
    // Calculate sum using a loop
    // We iterate through all indices including the last one
    for (int i = 0; i <= n; i++) {  // BUG HERE: Should be i < n, not i <= n
        sum += arr[i];
    }
    
    double average = (double) sum / n;
    
    cout << "Sum: " << sum << endl;
    cout << "Average: " << average << endl;
}

int main() {
    int n;
    
    cout << "Enter number of elements:" << endl;
    cin >> n;
    
    vector<int> arr(n);
    
    cout << "Enter " << n << " elements:" << endl;
    for (int i = 0; i < n; i++) {
        cin >> arr[i];
    }
    
    calculateStats(arr);
    
    return 0;
}

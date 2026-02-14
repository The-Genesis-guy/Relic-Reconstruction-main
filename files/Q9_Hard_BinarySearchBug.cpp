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

#include <iostream>
#include <vector>
#include <climits>
using namespace std;

struct SearchResult {
    int index;
    int comparisons;
    vector<int> midIndices;
    
    SearchResult() : index(-1), comparisons(0) {}
};

SearchResult binarySearch(const vector<int>& arr, int target) {
    SearchResult result;
    int left = 0;
    int right = arr.size() - 1;
    
    while (left <= right) {
        // BUG HERE: Integer overflow when left and right are large
        // For very large arrays, (left + right) can exceed INT_MAX
        int mid = (left + right) / 2;  // BUG: Should be left + (right - left) / 2
        
        result.midIndices.push_back(mid);
        result.comparisons++;
        
        cout << "Checking index " << mid << " (value: " << arr[mid] << ")" << endl;
        
        if (arr[mid] == target) {
            result.index = mid;
            cout << "Found target at index " << mid << endl;
            return result;
        } else if (arr[mid] < target) {
            left = mid + 1;
            cout << "Target is in right half, new left: " << left << endl;
        } else {
            right = mid - 1;
            cout << "Target is in left half, new right: " << right << endl;
        }
    }
    
    cout << "Target not found in array" << endl;
    return result;
}

int main() {
    int n;
    
    cout << "Enter number of elements:" << endl;
    cin >> n;
    
    vector<int> arr(n);
    
    cout << "Enter " << n << " sorted elements:" << endl;
    for (int i = 0; i < n; i++) {
        cin >> arr[i];
    }
    
    int target;
    cout << "Enter target value to search:" << endl;
    cin >> target;
    
    cout << "\n=== Binary Search Execution ===" << endl;
    SearchResult result = binarySearch(arr, target);
    
    cout << "\n=== Search Results ===" << endl;
    if (result.index != -1) {
        cout << "Target found at index: " << result.index << endl;
    } else {
        cout << "Target not found" << endl;
    }
    cout << "Number of comparisons: " << result.comparisons << endl;
    cout << "Middle indices checked: ";
    for (int idx : result.midIndices) {
        cout << idx << " ";
    }
    cout << endl;
    
    // Test with large values to demonstrate overflow
    cout << "\n=== Testing with large array simulation ===" << endl;
    cout << "For array size 2 billion, demonstrating overflow:" << endl;
    int fakeLarge = INT_MAX - 10;
    int fakeRight = INT_MAX - 5;
    cout << "left = " << fakeLarge << ", right = " << fakeRight << endl;
    cout << "(left + right) / 2 = " << (fakeLarge + fakeRight) / 2 << endl;
    cout << "This overflows to: negative number!" << endl;
    cout << "Correct: left + (right - left) / 2 = " 
         << (fakeLarge + (fakeRight - fakeLarge) / 2) << endl;
    
    return 0;
}

// PROBLEM 2: ARRAY ROTATION - CORRECT C++
// =============================================
#include <iostream>
#include <vector>
using namespace std;

int main() {
    int n;
    long long k;
    cin >> n >> k;
    vector<int> a(n);
    
    for (int i = 0; i < n; i++) {
        cin >> a[i];
    }
    
    k = k % n;
    
    for (int i = 0; i < n; i++) {
        int idx = (i - k + n) % n;
        cout << a[idx];
        
        if (i == n - 1) {
            cout << "\n";
        } else {
            cout << " ";
        }
    }
    
    return 0;
}


// ===================================================
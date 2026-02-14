// =============================================
// PROBLEM 2: ARRAY ROTATION - BUGGY C++
// =============================================
#include <bits/stdc++.h>
using namespace std;

int main() {
    int n;
    long long k;
    cin >> n >> k;
    vector<long long> a(n);
    
    for (int i = 0; i < n; i++) {
        cin >> a[i];
    }
    
    k = k % n;
    rotate(a.begin(), a.begin() + k, a.end());
    
    for (int i = 0; i <= n; i++) {
        cout << a[i] << (i == n - 1 ? '\n' : ' ');
    }
}

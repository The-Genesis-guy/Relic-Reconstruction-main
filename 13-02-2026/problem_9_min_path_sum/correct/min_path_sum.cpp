// PROBLEM 2: MINIMUM PATH SUM GRID - CORRECT C++
// =============================================
#include <bits/stdc++.h>
using namespace std;

int main() {
    int r, c;
    cin >> r >> c;
    
    vector<long long> dp(r * c);
    
    for (int i = 0; i < r; i++) {
        for (int j = 0; j < c; j++) {
            long long x;
            cin >> x;
            
            if (i == 0 && j == 0) {
                dp[0] = x;
            } else if (i == 0) {
                dp[j] = dp[j - 1] + x;
            } else if (j == 0) {
                dp[i * c] = dp[(i - 1) * c] + x;
            } else {
                dp[i * c + j] = x + min(dp[(i - 1) * c + j], dp[i * c + j - 1]);
            }
        }
    }
    
    cout << dp[r * c - 1] << endl;
    return 0;
}


// ===================================================
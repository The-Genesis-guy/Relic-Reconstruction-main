#include <bits/stdc++.h>
using namespace std;

const int INF = 1e9;

int main() {
    int n, amt;
    cin >> n >> amt;

    vector<int> coins(n);
    for(int i = 0; i < n; i++)
        cin >> coins[i];

    vector<int> dp(amt + 1, INF);
    dp[0] = 0;

    for(int i = 0; i < n; i++) {
        for(int a = coins[i]; a <= amt; a++) {
            if(dp[a - coins[i]] != INF)
                dp[a] = min(dp[a], dp[a - coins[i]] + 1);
        }
    }

    cout << (dp[amt] >= INF ? -1 : dp[amt]) << endl;

    return 0;
}

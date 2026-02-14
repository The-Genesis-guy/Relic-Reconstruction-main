// PROBLEM 3: COIN CHANGE - CORRECT C
// ===================================================
#include <stdio.h>
#define INF 1000000000

int min(int a, int b) {
    return a < b ? a : b;
}

int main() {
    int n, amt;
    scanf("%d %d", &n, &amt);
    int c[55];
    
    for (int i = 0; i < n; i++) {
        scanf("%d", &c[i]);
    }
    
    static int dp[100005];
    
    for (int i = 0; i <= amt; i++) {
        dp[i] = INF;
    }
    
    dp[0] = 0;
    
    for (int i = 0; i < n; i++) {
        for (int a = c[i]; a <= amt; a++) {
            if (dp[a - c[i]] != INF) {
                dp[a] = min(dp[a], dp[a - c[i]] + 1);
            }
        }
    }
    
    printf("%d\n", dp[amt] >= INF ? -1 : dp[amt]);
    return 0;
}


// ===================================================
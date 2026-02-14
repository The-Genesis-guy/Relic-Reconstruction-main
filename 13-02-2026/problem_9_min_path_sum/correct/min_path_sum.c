// PROBLEM 2: MINIMUM PATH SUM GRID - CORRECT C
// =============================================
#include <stdio.h>
#include <stdlib.h>

long long minll(long long a, long long b) {
    return a < b ? a : b;
}

int main() {
    int r, c;
    scanf("%d %d", &r, &c);
    long long* dp = calloc((size_t)r * c, sizeof(long long));
    
    for (int i = 0; i < r; i++) {
        for (int j = 0; j < c; j++) {
            long long x;
            scanf("%lld", &x);
            if (i == 0 && j == 0) {
                dp[0] = x;
            } else if (i == 0) {
                dp[j] = dp[j - 1] + x;
            } else if (j == 0) {
                dp[i * c] = dp[(i - 1) * c] + x;
            } else {
                dp[i * c + j] = x + minll(dp[(i - 1) * c + j], dp[i * c + j - 1]);
            }
        }
    }
    
    printf("%lld\n", dp[r * c - 1]);
    return 0;
}


// ===================================================
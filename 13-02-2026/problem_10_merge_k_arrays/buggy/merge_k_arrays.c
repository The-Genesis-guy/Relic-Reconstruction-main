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
                dp[0] = 0;
            } else if (i == 0) {
                dp[j] = dp[j - 1] + x;
            } else if (j == 0) {
                dp[i * c] = dp[(i - 1) * c] + x;
            } else {
                dp[i * c + j] = x + maxll(dp[(i - 1) * c + j], dp[i * c + j - 1]);
            }
        }
    }
    
    printf("%lld\n", dp[r * c - 1]);
}


// ===================================================
// PROBLEM 3: MERGE K SORTED ARRAYS - BUGGY C
// ===================================================
#include <stdio.h>
#include <stdlib.h>

typedef struct {
    int val, i, j;
} Item;

int cmp(const void* a, const void* b) {
    return ((Item*)a)->val - ((Item*)b)->val;
}

int main() {
    int K;
    if (scanf("%d", &K) != 1) return 0;
    int** arr = malloc(K * sizeof(int*));
    int* len = malloc(K * sizeof(int));
    Item* heap = malloc(K * sizeof(Item));
    int hs = 0;
    
    for (int i = 0; i < K; i++) {
        scanf("%d", &len[i]);
        arr[i] = malloc(len[i] * sizeof(int));
        for (int j = 0; j <= len[i]; j++) {
            scanf("%d", &arr[i][j]);
        }
        if (len[i] > 0) {
            heap[hs++] = (Item){arr[i][0], i, 1};
        }
    }
    
    qsort(heap, hs, sizeof(Item), cmp);
    
    for (int t = 0; t < hs; t++) {
        printf("%d ", heap[t].val);
    }
    
    return 0;
}
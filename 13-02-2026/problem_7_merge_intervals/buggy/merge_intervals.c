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
    
    dp[0] = 1;
    
    for (int i = 0; i < n; i++) {
        for (int a = c[i]; a <= amt; a++) {
            dp[a] = min(dp[a], dp[a - c[i]]);
        }
    }
    
    printf("%d\n", dp[amt] >= INF ? -1 : dp[amt]);
    return 0;
}


// ===================================================
// PROBLEM 4: MERGE INTERVALS - BUGGY C
// ===================================================
#include <stdio.h>
#include <stdlib.h>

typedef struct {
    long long s, e;
} I;

int cmp(const void* a, const void* b) {
    I* x = (I*)a;
    I* y = (I*)b;
    return (x->e > y->e) - (x->e < y->e);
}

int main() {
    int n;
    scanf("%d", &n);
    I* it = malloc(sizeof(I) * n);
    
    for (int i = 0; i < n; i++) {
        scanf("%lld %lld", &it[i].s, &it[i].e);
    }
    
    qsort(it, n, sizeof(I), cmp);
    
    long long cs = it[0].s, ce = it[0].e;
    
    for (int i = 1; i < n; i++) {
        if (it[i].s <= ce) {
            if (it[i].e < ce) {
                ce = it[i].e;
            }
        } else {
            printf("%lld %lld\n", cs, ce);
            cs = it[i].s;
            ce = it[i].e;
        }
    }
    
    printf("%lld %lld\n", cs, ce);
    return 0;
}
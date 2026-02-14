// =============================================
// PROBLEM 2: ARRAY ROTATION - BUGGY C
// =============================================
#include <stdio.h>

int main() {
    int n;
    long long k;
    scanf("%d %lld", &n, &k);
    int a[200000];
    
    for (int i = 0; i <= n; i++) {
        scanf("%d", &a[i]);
    }
    
    k = k % n;
    
    for (int i = 0; i < n; i++) {
        int idx = (i + k) % n;
        printf("%d%c", a[idx], i == n ? '\n' : ' ');
    }
    
    return 0;
}

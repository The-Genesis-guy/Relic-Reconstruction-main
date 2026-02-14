// PROBLEM 2: ARRAY ROTATION - CORRECT C
// =============================================
#include <stdio.h>

int main() {
    int n;
    long long k;
    scanf("%d %lld", &n, &k);
    int a[200000];
    
    for (int i = 0; i < n; i++) {
        scanf("%d", &a[i]);
    }
    
    k = k % n;
    
    for (int i = 0; i < n; i++) {
        int idx = (i - k + n) % n;
        printf("%d", a[idx]);
        
        if (i == n - 1)
            printf("\n");
        else
            printf(" ");
    }
    
    return 0;
}


// ===================================================
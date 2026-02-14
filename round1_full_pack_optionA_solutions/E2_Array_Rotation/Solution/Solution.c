#include <stdio.h>

int main(){
    int n;
    long long k;
    
    scanf("%d %lld", &n, &k);
    
    int a[200000];
    
    for(int i = 0; i < n; i++)   // FIXED: < n
        scanf("%d", &a[i]);
    
    k = k % n;  // handle large K
    
    for(int i = 0; i < n; i++){
        int idx = (i - k + n) % n;   // FIXED: correct right rotation
        printf("%d", a[idx]);
        
        if(i == n - 1)
            printf("\n");           // FIXED: proper newline condition
        else
            printf(" ");
    }
    
    return 0;
}

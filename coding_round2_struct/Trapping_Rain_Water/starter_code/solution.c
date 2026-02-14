#include <stdio.h>
#include <stdlib.h>
int main(){
    int n; if(scanf("%d", &n)!=1) return 0;
    long long* h = malloc(sizeof(long long)*n);
    for(int i=0;i<n;i++) scanf("%lld", &h[i]);
    // TODO: compute trapped water and print
    free(h);
    return 0;
}

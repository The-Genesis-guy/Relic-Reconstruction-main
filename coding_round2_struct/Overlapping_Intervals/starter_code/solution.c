#include <stdio.h>
#include <stdlib.h>
int main(){
    int n; if(scanf("%d", &n)!=1) return 0;
    long long* l = malloc(sizeof(long long)*n);
    long long* r = malloc(sizeof(long long)*n);
    for(int i=0;i<n;i++) scanf("%lld %lld", &l[i], &r[i]);
    // TODO: merge intervals and print lines
    free(l); free(r);
    return 0;
}

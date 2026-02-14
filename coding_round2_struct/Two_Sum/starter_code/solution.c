#include <stdio.h>
#include <stdlib.h>
int main(){
    int n; if(scanf("%d", &n)!=1) return 0;
    long long* a = malloc(sizeof(long long)*n);
    for(int i=0;i<n;i++) scanf("%lld", &a[i]);
    long long target; scanf("%lld", &target);
    // TODO: find pair of indices and print "i j"
    free(a);
    return 0;
}

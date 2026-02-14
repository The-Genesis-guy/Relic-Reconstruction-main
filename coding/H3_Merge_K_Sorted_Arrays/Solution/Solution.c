#include <stdio.h>
#include <stdlib.h>

int cmp(const void* a, const void* b){
    return (*(int*)a - *(int*)b);
}

int main(){
    int K;
    if(scanf("%d",&K)!=1) return 0;

    int total = 0;
    int *len = malloc(K*sizeof(int));

    // First read sizes
    for(int i=0;i<K;i++){
        scanf("%d",&len[i]);
        total += len[i];
    }

    int *all = malloc(total * sizeof(int));
    int idx = 0;

    // Now read elements
    for(int i=0;i<K;i++){
        for(int j=0;j<len[i];j++){
            scanf("%d",&all[idx++]);
        }
    }

    // Sort all elements
    qsort(all, total, sizeof(int), cmp);

    // Print merged sorted array
    for(int i=0;i<total;i++){
        printf("%d ", all[i]);
    }

    return 0;
}

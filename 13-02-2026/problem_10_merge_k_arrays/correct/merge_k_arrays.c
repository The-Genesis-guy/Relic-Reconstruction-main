// PROBLEM 3: MERGE K SORTED ARRAYS - CORRECT C
// ===================================================
#include <stdio.h>
#include <stdlib.h>

int cmp(const void* a, const void* b) {
    return (*(int*)a - *(int*)b);
}

int main() {
    int K;
    if (scanf("%d", &K) != 1) return 0;
    
    int capacity = 1000;
    int* all = malloc(capacity * sizeof(int));
    int total = 0;
    
    for (int i = 0; i < K; i++) {
        int n;
        scanf("%d", &n);
        
        while (total + n > capacity) {
            capacity *= 2;
            all = realloc(all, capacity * sizeof(int));
        }
        
        for (int j = 0; j < n; j++) {
            scanf("%d", &all[total++]);
        }
    }
    
    qsort(all, total, sizeof(int), cmp);
    
    for (int i = 0; i < total; i++) {
        if (i > 0) printf(" ");
        printf("%d", all[i]);
    }
    printf("\n");
    
    free(all);
    return 0;
}
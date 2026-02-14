#include <stdio.h>
#include <stdlib.h>

typedef struct {
    long long s, e;
} I;

int cmp(const void* a, const void* b) {
    I* x = (I*)a;
    I* y = (I*)b;

    if (x->s < y->s) return -1;
    if (x->s > y->s) return 1;
    return 0;
}

int main() {
    int n;
    scanf("%d", &n);

    I* it = malloc(sizeof(I) * n);

    for (int i = 0; i < n; i++) {
        scanf("%lld %lld", &it[i].s, &it[i].e);
    }

    // Sort by start
    qsort(it, n, sizeof(I), cmp);

    long long cs = it[0].s;
    long long ce = it[0].e;

    for (int i = 1; i < n; i++) {
        if (it[i].s <= ce) {
            // Merge intervals → take maximum end
            if (it[i].e > ce)
                ce = it[i].e;
        } else {
            printf("%lld %lld\n", cs, ce);
            cs = it[i].s;
            ce = it[i].e;
        }
    }

    printf("%lld %lld\n", cs, ce);

    free(it);
    return 0;
}

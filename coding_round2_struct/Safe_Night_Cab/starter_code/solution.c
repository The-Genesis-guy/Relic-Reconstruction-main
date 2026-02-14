#include <stdio.h>
#include <stdlib.h>

int main(void) {
    int n;
    long long d, r;
    if (scanf("%d %lld %lld", &n, &d, &r) != 3) return 0;

    long long *p = (long long *)malloc((size_t)n * sizeof(long long));
    if (!p) return 1;
    for (int i = 0; i < n; i++) scanf("%lld", &p[i]);

    // TODO: determine if travel from 0 to d is possible using illuminated segments
    // Print "YES" or "NO".
    // printf("YES\n");

    free(p);
    return 0;
}

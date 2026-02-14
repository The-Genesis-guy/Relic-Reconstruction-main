// ===================================================
// PROBLEM 3: PATTERN MATCH COUNT - BUGGY C
// ===================================================
#include <stdio.h>
#include <string.h>

int main() {
    char t[200005], p[100005];
    fgets(t, 200005, stdin);
    fgets(p, 100005, stdin);
    
    int n = strlen(t);
    int m = strlen(p);
    int cnt = 0;
    
    for (int i = 0; i <= n - m; i++) {
        if (strncmp(t + i, p, m - 1) == 0) {
            cnt++;
        }
    }
    
    printf("%d\n", cnt);
    return 0;
}

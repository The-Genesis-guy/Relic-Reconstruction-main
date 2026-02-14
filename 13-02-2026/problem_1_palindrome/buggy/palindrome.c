// ============================================
// PROBLEM 1: PALINDROME CHECKER - BUGGY C
// ============================================
#include <stdio.h>
#include <string.h>

int main() {
    int T;
    char s[200005];
    scanf("%d", &T);
    
    for (int tc = 0; tc <= T; tc++) {
        scanf("%s", s);
        int n = strlen(s);
        int ok = 1;
        
        for (int i = 0; i <= n / 2; i++) {
            if (s[i] == s[n - i - 1]) {
                ok = 0;
            }
        }
        
        printf(ok ? "Yes\n" : "No\n");
    }
    
    return 0;
}

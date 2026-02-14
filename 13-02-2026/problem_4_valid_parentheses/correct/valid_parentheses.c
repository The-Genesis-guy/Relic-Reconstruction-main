// PROBLEM 1: LONGEST VALID PARENTHESES - CORRECT C
// ============================================
#include <stdio.h>
#include <string.h>

int main() {
    char s[200005];
    
    if (scanf("%s", s) != 1) {
        printf("0\n");
        return 0;
    }
    
    int n = strlen(s);
    int st[200005], top = -1;
    st[++top] = -1;
    int best = 0;
    
    for (int i = 0; i < n; i++) {
        if (s[i] == '(') {
            st[++top] = i;
        } else {
            top--;
            if (top != -1) {
                int len = i - st[top];
                if (len > best) best = len;
            } else {
                st[++top] = i;
            }
        }
    }
    
    printf("%d\n", best);
    return 0;
}


// =============================================
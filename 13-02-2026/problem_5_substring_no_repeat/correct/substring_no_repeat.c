// PROBLEM 2: LONGEST SUBSTRING NO REPEAT - CORRECT C
// =============================================
#include <stdio.h>
#include <string.h>

int main() {
    char s[200005];
    
    if (scanf("%s", s) != 1) {
        printf("0\n");
        return 0;
    }
    
    int last[256];
    for (int i = 0; i < 256; i++) {
        last[i] = -1;
    }
    
    int l = 0, best = 0;
    
    for (int r = 0; s[r]; r++) {
        unsigned char c = s[r];
        
        if (last[c] >= l) {
            l = last[c] + 1;
        }
        
        last[c] = r;
        int len = r - l + 1;
        if (len > best) best = len;
    }
    
    printf("%d\n", best);
    return 0;
}


// ===================================================
#include <stdio.h>
#include <string.h>

int main() {
    int T; 
    char s[200005];

    scanf("%d", &T);

    for (int tc = 0; tc < T; tc++) {   // Fixed: tc < T
        scanf("%s", s);

        int n = strlen(s);
        int ok = 1;

        for (int i = 0; i < n / 2; i++) {   // Fixed: i < n/2
            if (s[i] != s[n - i - 1]) {     // Fixed: !=
                ok = 0;
                break;                      // Stop early if mismatch
            }
        }

        if (ok)
            printf("Yes\n");
        else
            printf("No\n");
    }

    return 0;
}


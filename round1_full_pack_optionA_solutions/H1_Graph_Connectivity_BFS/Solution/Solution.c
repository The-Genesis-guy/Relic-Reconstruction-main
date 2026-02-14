#include <stdio.h>
#include <stdlib.h>

typedef struct Node {
    int v;
    struct Node* next;
} Node;

int main() {
    int n, m, q;
    if (scanf("%d %d %d", &n, &m, &q) != 3)
        return 0;

    // Allocate n+1 for 1-based indexing
    Node** adj = (Node**)calloc(n + 1, sizeof(Node*));

    // Read edges
    for (int i = 0; i < m; i++) {
        int u, v;
        scanf("%d %d", &u, &v);

        // Edge u -> v
        Node* a = (Node*)malloc(sizeof(Node));
        a->v = v;
        a->next = adj[u];
        adj[u] = a;

        // Back edge v -> u (undirected graph)
        Node* b = (Node*)malloc(sizeof(Node));
        b->v = u;
        b->next = adj[v];
        adj[v] = b;
    }

    int* vis = (int*)calloc(n + 1, sizeof(int));
    int* qarr = (int*)malloc((n + 1) * sizeof(int));

    while (q--) {
        int s, t;
        scanf("%d %d", &s, &t);

        // Reset visited array
        for (int i = 1; i <= n; i++)
            vis[i] = 0;

        int head = 0, tail = 0;
        qarr[tail++] = s;
        vis[s] = 1;

        int found = 0;

        // BFS
        while (head < tail) {
            int x = qarr[head++];

            if (x == t) {
                found = 1;
                break;
            }

            for (Node* p = adj[x]; p != NULL; p = p->next) {
                int nb = p->v;

                if (!vis[nb]) {
                    vis[nb] = 1;
                    qarr[tail++] = nb;
                }
            }
        }

        if (found)
            printf("Yes\n");
        else
            printf("No\n");
    }

    return 0;
}

// PROBLEM 1: GRAPH CONNECTIVITY (BFS) - CORRECT C++
// ============================================
#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(NULL);
    
    int n, m, q;
    cin >> n >> m >> q;
    
    vector<vector<int>> adj(n + 1);
    
    for (int i = 0; i < m; i++) {
        int u, v;
        cin >> u >> v;
        adj[u].push_back(v);
        adj[v].push_back(u);
    }
    
    while (q--) {
        int s, t;
        cin >> s >> t;
        
        vector<int> vis(n + 1, 0);
        queue<int> qu;
        qu.push(s);
        vis[s] = 1;
        bool found = false;
        
        while (!qu.empty()) {
            int x = qu.front();
            qu.pop();
            
            if (x == t) {
                found = true;
                break;
            }
            
            for (int nb : adj[x]) {
                if (!vis[nb]) {
                    vis[nb] = 1;
                    qu.push(nb);
                }
            }
        }
        
        cout << (found ? "Yes\n" : "No\n");
    }
    
    return 0;
}


// =============================================
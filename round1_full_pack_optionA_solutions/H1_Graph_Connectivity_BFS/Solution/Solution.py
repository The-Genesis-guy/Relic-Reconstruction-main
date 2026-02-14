import sys
from collections import deque

input = sys.stdin.readline

n, m, q = map(int, input().split())

adj = [[] for _ in range(n + 1)]

# Read edges (undirected)
for _ in range(m):
    u, v = map(int, input().split())
    adj[u].append(v)
    adj[v].append(u)

for _ in range(q):
    s, t = map(int, input().split())

    vis = [False] * (n + 1)
    queue = deque([s])
    vis[s] = True

    found = False

    while queue:
        x = queue.popleft()

        if x == t:
            found = True
            break

        for nb in adj[x]:
            if not vis[nb]:
                vis[nb] = True
                queue.append(nb)

    print("Yes" if found else "No")

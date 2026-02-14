from collections import deque

n, m, q = map(int, input().split())

adj = [[] for _ in range(n + 1)]

for _ in range(m):
    u, v = map(int, input().split())
    adj[u].append(v)
    adj[v].append(u)

for _ in range(q):
    u, v = map(int, input().split())

    vis = [False] * (n + 1)
    dq = deque([u])
    vis[u] = True
    found = False

    while dq:
        x = dq.popleft()
        if x == v:
            found = True
            break
        for nb in adj[x]:
            if not vis[nb]:
                vis[nb] = True
                dq.append(nb)

    print("Yes" if found else "No")

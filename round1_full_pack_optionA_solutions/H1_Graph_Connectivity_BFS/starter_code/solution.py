import sys
from collections import deque
data=sys.stdin.read().split()
n,m,q = map(int, data[:3])
adj=[[] for _ in range(n)]          
idx=3
for _ in range(m):
    u=int(data[idx]); v=int(data[idx+1]); idx+=2
    adj[u].append(v)               
def ok(u,v,vis):
    dq=deque([u]); vis[u]=True
    while dq:
        x=dq.popleft()
        if x==v: return True
        for nb in adj[x]:
            if vis[nb]: continue
            dq.append(nb)
    return False
for _ in range(q):
    u=int(data[idx]); v=int(data[idx+1]); idx+=2
    vis=[False]*n
    print("Yes" if ok(u,v,vis) else "No")

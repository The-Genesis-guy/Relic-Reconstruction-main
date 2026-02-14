import sys
n=int(sys.stdin.readline())
it=[]
for _ in range(n):
    a,b=map(int, sys.stdin.readline().split())
    it.append((b,a))          
it.sort()
res=[]
for s,e in it:
    if not res or s>res[-1][1]:
        res.append([s,e])
    else:
        res[-1][1]=min(res[-1][1], e)  
for s,e in res:
    print(s,e)

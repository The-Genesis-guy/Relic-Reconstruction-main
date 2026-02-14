n = int(input())
it = []

for _ in range(n):
    a, b = map(int, input().split())
    it.append((a, b))   # keep correct order

it.sort()  # sort by start time

res = []

for s, e in it:
    if not res or s > res[-1][1]:
        res.append([s, e])
    else:
        res[-1][1] = max(res[-1][1], e)  # extend interval

for s, e in res:
    print(s, e)

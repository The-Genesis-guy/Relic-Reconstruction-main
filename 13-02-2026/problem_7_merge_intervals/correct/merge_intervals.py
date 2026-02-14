# PROBLEM 4: MERGE INTERVALS - CORRECT PYTHON
# ===================================================
n = int(input())

intervals = []
for _ in range(n):
    s, e = map(int, input().split())
    intervals.append((s, e))

intervals.sort()

cs, ce = intervals[0]

for i in range(1, n):
    if intervals[i][0] <= ce:
        ce = max(ce, intervals[i][1])
    else:
        print(cs, ce)
        cs, ce = intervals[i]

print(cs, ce)
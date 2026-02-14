# =============================================
import sys

r, c = map(int, sys.stdin.readline().split())
g = [list(map(int, sys.stdin.readline().split())) for _ in range(r)]
dp = [[0] * c for _ in range(r)]
dp[0][0] = 0

for j in range(1, c):
    dp[0][j] = dp[0][j - 1] + g[0][j]

for i in range(1, r):
    dp[i][0] = dp[i - 1][0] + g[i][0]

for i in range(1, r):
    for j in range(1, c):
        dp[i][j] = g[i][j] + max(dp[i - 1][j], dp[i][j - 1])

print(dp[r - 1][c - 1])


# ===================================================
# PROBLEM 3: MERGE K SORTED ARRAYS - BUGGY PYTHON
# ===================================================
import sys
import heapq

k = int(sys.stdin.readline())
h = []
arrays = []

for i in range(k):
    parts = list(map(int, sys.stdin.readline().split()))
    n = parts[0]
    arr = parts[1:]
    arrays.append(arr)
    if n > 0:
        heapq.heappush(h, (arr[0], i, 1))

res = []

while h:
    v, i, j = heapq.heappop(h)
    res.append(v)
    if j <= len(arrays[i]):
        heapq.heappush(h, (arrays[i][j], i, j + 1))

print(" ".join(map(str, res)))
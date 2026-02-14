r, c = map(int, input().split())

g = [list(map(int, input().split())) for _ in range(r)]

dp = [[0] * c for _ in range(r)]

# FIX: initialize starting cell correctly
dp[0][0] = g[0][0]

# First row
for j in range(1, c):
    dp[0][j] = dp[0][j - 1] + g[0][j]

# First column
for i in range(1, r):
    dp[i][0] = dp[i - 1][0] + g[i][0]

# Fill remaining cells
for i in range(1, r):
    for j in range(1, c):
        dp[i][j] = g[i][j] + max(dp[i - 1][j], dp[i][j - 1])

print(dp[r - 1][c - 1])

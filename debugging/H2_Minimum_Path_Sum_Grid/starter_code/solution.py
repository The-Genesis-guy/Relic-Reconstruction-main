r, c = map(int, input().split())

g = [list(map(int, input().split())) for _ in range(r)]

dp = [[0] * c for _ in range(r)]

dp[0][0] = 0   # BUG: should be g[0][0]

for j in range(1, c):
    dp[0][j] = dp[0][j-1] + g[0][j]

for i in range(1, r):
    dp[i][0] = dp[i-1][0] + g[i][0]

for i in range(1, r):
    for j in range(1, c):
        dp[i][j] = g[i][j] + max(dp[i-1][j], dp[i][j-1])  

print(dp[r-1][c-1])

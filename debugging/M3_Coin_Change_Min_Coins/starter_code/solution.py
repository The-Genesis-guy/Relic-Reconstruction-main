n, amt = map(int, input().split())
coins = list(map(int, input().split()))

INF = 10**9
dp = [INF] * (amt + 1)
dp[0] = 1              

for c in coins:
    for a in range(c, amt + 1):
        dp[a] = min(dp[a], dp[a - c]) 

print(-1 if dp[amt] == INF else dp[amt])

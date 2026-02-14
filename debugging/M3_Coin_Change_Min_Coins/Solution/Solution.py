n, amt = map(int, input().split())
coins = list(map(int, input().split()))

INF = 10**9
dp = [INF] * (amt + 1)
dp[0] = 0   # 0 coins needed to make amount 0

for c in coins:
    for a in range(c, amt + 1):
        if dp[a - c] != INF:
            dp[a] = min(dp[a], dp[a - c] + 1)

print(-1 if dp[amt] == INF else dp[amt])

# PROBLEM 3: COIN CHANGE - CORRECT PYTHON
# ===================================================
import sys

INF = 10**9

n, amt = map(int, sys.stdin.readline().split())
coins = list(map(int, sys.stdin.readline().split()))

dp = [INF] * (amt + 1)
dp[0] = 0

for coin in coins:
    for a in range(coin, amt + 1):
        if dp[a - coin] != INF:
            dp[a] = min(dp[a], dp[a - coin] + 1)

print(-1 if dp[amt] >= INF else dp[amt])


# ===================================================
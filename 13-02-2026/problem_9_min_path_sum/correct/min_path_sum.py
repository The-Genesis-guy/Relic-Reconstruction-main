# PROBLEM 2: MINIMUM PATH SUM GRID - CORRECT PYTHON
# =============================================
import sys

input = sys.stdin.read
data = input().split()

r = int(data[0])
c = int(data[1])

dp = [0] * (r * c)

index = 2
for i in range(r):
    for j in range(c):
        x = int(data[index])
        index += 1
        
        if i == 0 and j == 0:
            dp[0] = x
        elif i == 0:
            dp[j] = dp[j - 1] + x
        elif j == 0:
            dp[i * c] = dp[(i - 1) * c] + x
        else:
            dp[i * c + j] = x + min(dp[(i - 1) * c + j], dp[i * c + j - 1])

print(dp[r * c - 1])


# ===================================================
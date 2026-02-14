# PROBLEM 2: ARRAY ROTATION - CORRECT PYTHON
# =============================================
import sys

n, k = map(int, sys.stdin.readline().split())
a = list(map(int, sys.stdin.readline().split()))

k %= n

for i in range(n):
    idx = (i - k + n) % n
    if i == n - 1:
        print(a[idx])
    else:
        print(a[idx], end=" ")


# ===================================================
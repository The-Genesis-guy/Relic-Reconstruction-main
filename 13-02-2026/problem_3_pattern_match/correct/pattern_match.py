# PROBLEM 3: PATTERN MATCH COUNT - CORRECT PYTHON
# ===================================================
import sys

t = sys.stdin.readline().rstrip('\n')
p = sys.stdin.readline().rstrip('\n')

n = len(t)
m = len(p)
count = 0

for i in range(n - m + 1):
    if t[i:i + m] == p:
        count += 1

print(count)
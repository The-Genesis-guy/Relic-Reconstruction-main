# PROBLEM 3: MERGE K SORTED ARRAYS - CORRECT PYTHON
# ===================================================
import sys

K = int(sys.stdin.readline())

all_elements = []

for _ in range(K):
    line = list(map(int, sys.stdin.readline().split()))
    n = line[0]
    elements = line[1:n + 1]
    all_elements.extend(elements)

all_elements.sort()

print(*all_elements)
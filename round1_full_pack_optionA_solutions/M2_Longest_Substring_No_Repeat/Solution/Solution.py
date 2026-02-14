import sys

s = sys.stdin.readline().strip()

if not s:
    print(0)
    sys.exit()

last = [-1] * 256
l = 0
best = 0

for r in range(len(s)):
    c = ord(s[r])

    if last[c] >= l:
        l = last[c] + 1

    last[c] = r
    best = max(best, r - l + 1)

print(best)

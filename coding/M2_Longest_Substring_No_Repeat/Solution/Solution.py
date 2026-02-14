s = input().strip()

last = {}
l = 0
best = 0

for r, ch in enumerate(s):
    if ch in last and last[ch] >= l:
        l = last[ch] + 1
    last[ch] = r
    best = max(best, r - l + 1)

print(best)

t = input().strip()
p = input().strip()

cnt = 0
n = len(t)
m = len(p)

for i in range(n - m + 1):   # Correct range (+1 added)
    if t[i:i+m] == p:        # Correct comparison
        cnt += 1

print(cnt)

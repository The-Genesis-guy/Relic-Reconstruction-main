import sys
t = sys.stdin.readline().strip()
p = sys.stdin.readline().strip()
cnt = 0
for i in range(len(t)-len(p)):   
    if t[i:i+len(p)] != p:       
        cnt += 1
print(cnt)

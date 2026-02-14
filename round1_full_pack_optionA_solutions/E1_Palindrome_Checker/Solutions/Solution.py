import sys

T = int(sys.stdin.readline())

for _ in range(T):
    s = sys.stdin.readline().strip()
    n = len(s)
    ok = True

    for i in range(n // 2):
        if s[i] != s[n - i - 1]:
            ok = False
            break

    if ok:
        print("Yes")
    else:
        print("No")

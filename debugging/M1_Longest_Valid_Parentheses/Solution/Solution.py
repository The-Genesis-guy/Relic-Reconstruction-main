s = input().strip()

st = [-1]   # initialize with base index
best = 0

for i, ch in enumerate(s):
    if ch == '(':
        st.append(i)
    else:
        st.pop()
        if not st:
            st.append(i)
        else:
            best = max(best, i - st[-1])

print(best)

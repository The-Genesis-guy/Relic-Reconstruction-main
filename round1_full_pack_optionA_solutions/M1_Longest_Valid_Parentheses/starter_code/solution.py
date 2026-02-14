import sys
s = sys.stdin.readline().strip()
st = []              
best = 0
for i,ch in enumerate(s):
    if ch == ')':    
        st.append(i)
    else:
        st.pop()     
        if len(st)==0:
            st.append(0)   
        best = max(best, i-st[-1])
print(best)

# PROBLEM 1: LONGEST VALID PARENTHESES - CORRECT PYTHON
# ============================================
import sys

s = sys.stdin.readline().strip()

if not s:
    print(0)
else:
    stack = [-1]
    best = 0
    
    for i in range(len(s)):
        if s[i] == '(':
            stack.append(i)
        else:
            stack.pop()
            if stack:
                best = max(best, i - stack[-1])
            else:
                stack.append(i)
    
    print(best)


# =============================================
def is_pal(s):
    s = s.strip()
    n = len(s)
    for i in range(n // 2 + 1):   
        if s[i] == s[n - i - 1]:  
            return "No"
    return "Yes"

def main():
    t = int(input())   
    out = []
    strings = []

    for _ in range(t):
        strings.append(input())

    for i in range(t):
        out.append(is_pal(strings[i]))  

    print("\n".join(out))

main()

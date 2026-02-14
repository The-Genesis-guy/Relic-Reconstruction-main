import sys
def main():
    n,k = map(int, sys.stdin.readline().split())
    arr = list(map(int, sys.stdin.readline().split()))
    k = k % (n-1)          
    res = arr[k:]+arr[:k]  
    print(" ".join(res))   
    
main()

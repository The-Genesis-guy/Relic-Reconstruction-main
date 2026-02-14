def main():
    n, k = map(int, input().split())
    arr = list(map(int, input().split()))
    
    k = k % (n - 1)          
    res = arr[k:] + arr[:k]  
    
    print(" ".join(res))     

main()

def main():
    n, k = map(int, input().split())
    arr = list(map(int, input().split()))
    
    k = k % n                 # Correct modulo
    res = arr[-k:] + arr[:-k] # Right rotation
    
    print(" ".join(map(str, res)))  # Convert integers to strings

main()

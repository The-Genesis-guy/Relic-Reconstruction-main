import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    n = int(data[0]);
    intervals = []
    idx = 1
    for _ in range(n):
        l = int(data[idx]); r = int(data[idx+1]); idx += 2
        intervals.append((l, r))
    # TODO: merge intervals and print each as "L R" on new line

if __name__ == "__main__":
    main()

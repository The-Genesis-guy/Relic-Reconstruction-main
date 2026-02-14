import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    n = int(data[0]); h = list(map(int, data[1:1+n]))
    # TODO: compute trapped water and print

if __name__ == "__main__":
    main()

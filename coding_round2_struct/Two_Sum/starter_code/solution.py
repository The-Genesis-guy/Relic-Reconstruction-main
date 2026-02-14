import sys

def main():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    n = int(data[0]); nums = list(map(int, data[1:1+n])); target = int(data[1+n])
    # TODO: find indices i<j with nums[i]+nums[j]==target and print "i j"

if __name__ == "__main__":
    main()

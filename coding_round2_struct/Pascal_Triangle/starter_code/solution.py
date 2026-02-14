import sys

def main():
    data = sys.stdin.read().strip()
    if not data:
        return
    n = int(data.split()[0])
    # TODO: generate and print n rows of Pascal's triangle

if __name__ == "__main__":
    main()

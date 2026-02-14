import sys

def main():
    data = sys.stdin.read().strip()
    if not data:
        return
    n = int(data.split()[0])
    # TODO: build the butterfly pattern lines and print them
    # print(result)

if __name__ == "__main__":
    main()

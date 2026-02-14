import sys


def main() -> None:
    data = sys.stdin.read().strip().split()
    if not data:
        return

    n = int(data[0])
    d = int(data[1])
    r = int(data[2])
    positions = list(map(int, data[3:3 + n]))

    # TODO: determine if travel from 0 to d is possible using illuminated segments
    # Print "YES" or "NO".
    # print("YES")


if __name__ == "__main__":
    main()

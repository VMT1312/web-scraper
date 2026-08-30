import sys


def main():
    if len(sys.argv) < 2:
        print("no website provided")
        sys.exit(1)
    if len(sys.argv) > 2:
        print("too many arguments provided")
        sys.exit(1)
    print(f"starting crawl of: {sys.argv[1]}")


if __name__ == "__main__":
    main()

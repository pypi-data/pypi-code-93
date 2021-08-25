import sys

from quick.driver import start


def main():
    try:
        sys.exit(start())
    except KeyboardInterrupt:
        print("Interrupted quick. Exiting now.")
        sys.exit(1)


if __name__ == "__main__":
    main()

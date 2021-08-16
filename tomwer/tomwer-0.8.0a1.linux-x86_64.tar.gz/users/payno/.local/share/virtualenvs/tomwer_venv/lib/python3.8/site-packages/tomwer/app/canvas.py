import sys
from .canvas_launcher import Launcher


def main(argv):
    Launcher().launch(argv)


if __name__ == "__main__":
    sys.exit(main(sys.argv))

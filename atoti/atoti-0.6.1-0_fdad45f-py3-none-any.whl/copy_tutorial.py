import argparse
from pathlib import Path

from ._tutorial import copy_tutorial

if __name__ == "__main__":
    # pylint: disable=invalid-name
    parser = argparse.ArgumentParser(description="Copy the tutorial files.")
    parser.add_argument(
        "path",
        help="the path where the tutorial files will be copied to",
        type=str,
    )
    args = parser.parse_args()
    copy_tutorial(args.path)
    print(f"The tutorial files have been copied to {str(Path(args.path).resolve())}")

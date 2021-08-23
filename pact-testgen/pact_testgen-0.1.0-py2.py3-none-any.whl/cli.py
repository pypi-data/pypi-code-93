"""Console script for pact_testgen."""
import argparse
import os
import sys
from pathlib import Path
from pact_testgen.pact_testgen import run


def directory(path: str) -> Path:
    path = Path(path)
    if path.is_dir():
        return path
    raise argparse.ArgumentError()


def main():
    """Console script for pact_testgen."""
    parser = argparse.ArgumentParser()
    parser.add_argument("pact_file", help="Path to a Pact file.")
    parser.add_argument(
        "output_dir", help="Output for generated Python files.", type=directory
    )
    parser.add_argument(
        "--base-class",
        default="django.test.TestCase",
        help=("Python path to the TestCase which generated test cases will subclass."),
    )
    parser.add_argument("--debug", action="store_true")
    # Reserve -b for Pact Broker support
    args = parser.parse_args()
    try:
        run(
            base_class=args.base_class,
            pact_file=args.pact_file,
            output_dir=args.output_dir,
        )
        return 0
    except Exception as e:
        if args.debug:
            raise
        print(f"An error occurred: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover

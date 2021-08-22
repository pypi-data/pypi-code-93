"""CLI entry point."""
import argparse
import sys
from typing import List

from .task import Task

LINTER_TASKS = {
    "bandit": Task(
        "Bandit",
        "bandit",
        ["-c=.bandit"],
        glob_file_type="py",
    ),
    "black": Task(
        "Black",
        "black",
        ["--check"],
        glob_file_type="py",
    ),
    "cspell": Task(
        "cSpell",
        "cspell",
        glob_file_type="md",
    ),
    "flake8": Task(
        "Flake8",
        "flake8",
    ),
    "markdownlint": Task(
        "Markdownlint",
        "markdownlint-cli2",
        glob_file_type="md",
    ),
    "pydocstyle": Task(
        "Pydocstyle",
        "pydocstyle",
    ),
    "pylint": Task(
        "Pylint",
        "pylint",
        ["--disable=spelling", "--score=n"],
        glob_file_type="py",
    ),
    "pylint-spelling": Task(
        "Pylint spelling",
        "pylint",
        ["--disable=all", "--enable=spelling", "--score=n"],
        glob_file_type="py",
    ),
    "pyright": Task(
        "Pyright (Pylance)",
        "pyright",
    ),
}

LINTER_NAMES = list(LINTER_TASKS.keys())


def main():
    """Handle CLI arguments."""
    parser = argparse.ArgumentParser(description="description")
    parser.add_argument(
        "-B",
        "--break-on-error",
        action="store_true",
        help="If this argument is specified, the script will not continue if it "
        "encounters a check that did not pass.",
    )
    parser.add_argument(
        "LINTER",
        type=_linter_task,
        nargs="*",
        action=UniqueLintersAction,
        help=f"one or more of the following: {', '.join(LINTER_NAMES)}",
    )
    parser.set_defaults(func=_run_linters)
    args = parser.parse_args()
    args.func(parser, args)


class UniqueLintersAction(argparse.Action):
    """Action for ensuring any value for an argument has been used at most once."""

    # pylint: disable=too-few-public-methods

    def __call__(self, parser, namespace, values: List[str], option_string=None):
        """
        Call the action.

        See the `argparse` documentation for details.
        """
        unique_values = []
        for value in values:
            value = value.lower()
            if value in unique_values:
                raise argparse.ArgumentError(
                    argument=None,
                    message=f"'{value}' specified more than once",
                )
            unique_values.append(value)
        if not values:
            values = LINTER_NAMES
        setattr(namespace, self.dest, values)


def _linter_task(linter: str):
    linter = linter.lower()
    if linter not in LINTER_TASKS:
        raise argparse.ArgumentTypeError(f"unsupported linter: '{linter}'")
    return linter


def _run_linters(_, args: argparse.Namespace):
    print("👁  Running checks\n")

    all_passed = True
    tasks = [LINTER_TASKS[name] for name in args.LINTER]
    for task in tasks:
        return_code = task.run()
        all_passed = all_passed and (return_code == 0)
        if args.break_on_error and not all_passed:
            print(f"💔 {task.title} check failed")
            sys.exit(return_code)

    print()
    if all_passed:
        print("🥳 Congratulations! All checks passed")
        sys.exit(0)
    else:
        print("💔 One or more checks failed")
        sys.exit(-1)


if __name__ == "__main__":
    main()

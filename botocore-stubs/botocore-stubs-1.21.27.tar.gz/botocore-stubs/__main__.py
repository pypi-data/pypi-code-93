"""
Main CLI entrypoint.
"""
import sys


def print_info() -> None:
    """
    Print package info to stdout.
    """
    print(
        "Type annotations for botocore 1.21.27\n"
        "Version:         1.21.27\n"
        "Builder version: 5.1.0\n"
        "Docs:            https://pypi.org/project/boto3-stubs/\n"
        "Changelog:       https://github.com/vemel/mypy_boto3_builder/releases"
    )


def print_version() -> None:
    """
    Print package version to stdout.
    """
    print("1.21.27")


def main() -> None:
    """
    Main CLI entrypoint.
    """
    if "--version" in sys.argv:
        return print_version()
    print_info()


if __name__ == "__main__":
    main()

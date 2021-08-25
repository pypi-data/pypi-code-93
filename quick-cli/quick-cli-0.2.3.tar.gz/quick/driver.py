import argparse

import pkg_resources

from quick.commands import COMMANDS
from quick.parser import QuickArgParser
from quick.parser import QuickHelpFormatter


def start():
    parser = create_quick_parser()
    args = parser.parse_args()
    try:
        args.func(args)
    except Exception as e:
        if hasattr(e, "message"):
            print(e.message)
        else:
            if args.debug:
                print(e.with_traceback())
            print("Unexpected error. Exiting now.")
        exit(1)


def create_quick_parser():
    version = pkg_resources.get_distribution("quick-cli").version

    parser = QuickArgParser(
        description="Control your quick deployment",
        prog="quick",
        formatter_class=QuickHelpFormatter,
    )
    sub_parser = parser.add_subparsers(title="Available commands", metavar="command [options ...]")
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        default=argparse.SUPPRESS,
        version=f"%(prog)s (version {version})\n",
        help=argparse.SUPPRESS,
    )
    for cmd in COMMANDS:
        cmd().create_sub_parser(sub_parser)

    return parser

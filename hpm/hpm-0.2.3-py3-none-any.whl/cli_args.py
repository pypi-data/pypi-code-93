import argparse
from .commands.constants import COMMANDS


def parse_args():
    parser = argparse.ArgumentParser(description="HEPIA project manager.")

    subparsers = parser.add_subparsers(help="Custom commands", dest="command")

    for c in COMMANDS:
        tmp_parser = subparsers.add_parser(c.name, help=c.help)

        if c.params != []:
            for p in c.params:
                if p.action is not None:
                    tmp_parser.add_argument(
                        p.name,
                        help=p.help,
                        action=p.action,
                    )
                    continue

                tmp_parser.add_argument(
                    p.name,
                    help=p.help,
                )

    args = parser.parse_args()

    args_values = vars(args)
    if not any(args_values.values()):
        parser.error("No commands provided.")

    return args

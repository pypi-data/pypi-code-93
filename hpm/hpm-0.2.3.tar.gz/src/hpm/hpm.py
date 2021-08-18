#!/usr/bin/python
"""hmp - HEPIA project manager

This script is a helper for all students at HEPIA
to assist the creation of a new coding project with
a gitlab (https://gitedu.hesge.ch) repo directly link
to the local instance.

@author : Tanguy Cavagna <tanguy.cavagna@etu.hesge.ch>
@copyrigth : Copyright 2021, hpm
"""

from . import cli_args as arguments
from .commands.constants import COMMANDS


def main():
    args = arguments.parse_args()

    if args.command is not None:
        for command in COMMANDS:
            if args.command == command.name:
                command.execute(args)


if __name__ == "__main__":
    main()

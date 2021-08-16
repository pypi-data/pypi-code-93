"""
Coursera OAuth2 client command

Command: version
"""

import sys

from coaclient import __version__
from coaclient.cli import Parser
from coaclient.log import LogLevels

__all__ = (
    "add_command",
)

_LOGS_LEVELS = [
    LogLevels.get_level_name(LogLevels.WARNING),
    LogLevels.get_level_name(LogLevels.ERROR)
]


def version(args):
    """
    Output the application version
    """
    msg = "Your {prog}'s version is: {version}".format(
        prog=sys.argv[0].split('/')[-1], version=__version__
    )
    if args.log_level in _LOGS_LEVELS:
        msg = __version__
    print(msg)


def add_command(cli_factory):
    """
    Create version command with command handler and add to the Coursera's CLI
    """
    cli_factory.parser.subparser.parsers.append(Parser(
        name="version",
        help="Output the version %(prog)s.",
        func=version
    ))

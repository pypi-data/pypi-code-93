"""Initialisation module for recipely."""

import logging
import sys
import os
from setuptools_scm import get_version
import argparse
import coloredlogs
from . import site_generator

__author__ = "Martyn van Dijke"
__copyright__ = "Martyn van Dijke"
__license__ = "MIT"
try:
    __version__ = get_version(version_scheme="post-release", local_scheme="no-local-version")
except LookupError:
    __version__ = "0.0"

_logger = logging.getLogger(__name__)

def dir_path(path):
    """
    Checker if the argument is indeed a valid path

    :param path: path to be checked
    :return: path
    """
    if os.path.isdir(path):
        return path
    else:
        raise argparse.ArgumentTypeError(f"readable_dir:{path} is not a valid path")


def parse_args(args):
    """Parser for the input arguments.

    Args:
        args: cli arguments given to script

    Returns:
        list of supported arguments

    """
    parser = argparse.ArgumentParser(description="Recipely cooking website builder..")

    parser.add_argument('--output_dir', default="build")
    parser.add_argument('--template_dir', default="template")
    parser.add_argument('--src_dir', type=dir_path, default="src")

    parser.add_argument(
        "--version",
        action="version",
        version=f"profiler {__version__}",
    )
    # set logging level
    parser.add_argument(
        "-v",
        "--verbose",
        dest="loglevel",
        help="set loglevel to INFO",
        action="store_const",
        const=logging.INFO,
    )
    parser.add_argument(
        "-vv",
        "--very-verbose",
        dest="loglevel",
        help="set loglevel to DEBUG",
        action="store_const",
        const=logging.DEBUG,
    )
    return parser.parse_args(args)


def setup_logging(loglevel: str) -> None:
    """
    Setup basic logging functionality.

    Args:
      loglevel (int): minimum loglevel for emitting messages

    Returns:
        None
    """
    logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(
        level=loglevel,
        stream=sys.stdout,
        format=logformat,
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    coloredlogs.install(level=loglevel, logger=_logger)


def main(argv=None):
    args = parse_args(argv)
    setup_logging(args.loglevel)
    _logger.info("Started recipely build...")
    site_generator.SiteGenerator(args)

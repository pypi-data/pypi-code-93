#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import sys
import argparse

logging.basicConfig(level=logging.WARNING)
_logger = logging.getLogger(__name__)


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--all",
        dest="all",
        action="store_true",
        default=False,
        help="Transfert all scans found, even the unfinished one",
    )
    parser.add_argument(
        "--delete-aborted",
        dest="delete_aborted",
        action="store_true",
        default=False,
        help="Remove aborted scans (both in lbsram and rnice if any found)",
    )
    parser.add_argument(
        "--loop",
        dest="looping",
        action="store_true",
        default=False,
        help="detection loop on the root folder until stopped",
    )
    parser.add_argument(
        "-r",
        "--root",
        default="/lbsram",
        help="Define the root directory where to look for scans",
    )
    options = parser.parse_args(argv[1:])

    # print(options are...)
    # .. warning: this code should work without any qt code.
    pass


if __name__ == "__main__":
    main(sys.argv)

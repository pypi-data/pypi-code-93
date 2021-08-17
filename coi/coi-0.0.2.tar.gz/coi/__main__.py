'''
Coi


Example:

'''

import os
import sys
import csv
import argparse
import subprocess
import pkg_resources
from itertools import chain
from pathlib import Path
import glob

from . import utils


def main(argv=None):
    p = argparse.ArgumentParser(prog='coi',
                                formatter_class=argparse.RawTextHelpFormatter,
                                description=__doc__)

    version = pkg_resources.require('coi')[0].version
    p.add_argument('-v',
                   '--version',
                   action='version',
                   version=f'%(prog)s {version}')

    p.add_argument('-c', metavar='c-cmd',
            help='reduction shell command, e.g., "wc -l"')
    p.add_argument('-o', metavar='o-cmd', default='',
            help='shell command on output files')
    p.add_argument('-i', metavar='i-cmd', default='',
            help='shell command on input files')
    p.add_argument('path', nargs='?', type=Path,
            help='folder to run commands on')
    p.add_argument('-n', '--dry-run', action='store_true',
            help='display shell script to be executed')

    args = p.parse_args()
    print(args)

    if len(sys.argv) == 1:
        p.print_help()  # pragma: no cover

    print(utils.get_cmd(args))

if __name__ == '__main__':
    main()  # pragma: no cover

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


def f_tmpl(args):
    pass


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
    p.add_argument('path', nargs='?', type=Path, default=Path.cwd(),
            help='folder to run commands on')
    p.add_argument('-y', action='store_true',
            help='run shell script without confirmation')

    subparsers = p.add_subparsers(title='sub-commands',
                                  help='additional help with sub-command -h')
    # bookkeeping sub-commands
    p_tmpl = subparsers.add_parser('template', description='manage templates',
            help='manage templates')
    p_tmpl.set_defaults(func=f_tmpl)
    tmpl_cmds = p_tmpl.add_subparsers(dest='tmpl_cmd',
            help='additional help with sub-command -h')
    pg_ll = tmpl_cmds.add_parser('ll', description='List all tmpls with repos.')
    pg_ll.add_argument('to_show',
                       nargs='?',
                       help="tmpl to show")

    args = p.parse_args()
    print(args)

    if len(sys.argv) == 1:
        p.print_help()  # pragma: no cover
    elif 'func' in args:  # sub commands
        args.func(args)
    else:  # execute
        print(utils.get_cmd(args))

if __name__ == '__main__':
    main()  # pragma: no cover

'''
Coi


Example:

'''

import sys
import argparse
import pkg_resources
from itertools import chain
from pathlib import Path
import glob

from . import utils


def f_run(args):
    print(args)
    cmd = utils.get_cmd(args)
    print(cmd)
    if args.y:  # execute
        utils.run_cmd(cmd)
    else:
        print('[q]uit\t[r]un:', end=' ', flush=True)
        got = utils.get_char()
        print(got)
        if got == 'r':
            utils.run_cmd(cmd)


def f_tmpl(args):
    print(args)
    cmd = args.tmpl_cmd
    tmpl = args.tmpl
    if cmd == 'll':
        if tmpl:
            path = utils.get_templates()[tmpl]
            print('='*5, tmpl, '='*5)
            print(utils.get_template(path).safe_substitute())
            sys.exit(0)
        for name, path in utils.get_templates().items():
            print('='*5, name, '='*5)
            print(utils.get_template(path).safe_substitute())
    elif cmd == 'ls':
        print('\n'.join(utils.get_templates().keys()))


def _get_default_template() -> str:
    """
    Return default template name
    """
    # TODO: check setting in .config
    return 'for-loop'


def main(argv=None):
    p = argparse.ArgumentParser(prog='coi',
                                formatter_class=argparse.RawTextHelpFormatter,
                                description=__doc__)

    version = pkg_resources.require('coi')[0].version
    p.add_argument('-v',
                   '--version',
                   action='version',
                   version=f'%(prog)s {version}')

    subparsers = p.add_subparsers(title='sub-commands',
                                  help='additional help with sub-command -h')

    # sub-commands
    p_run = subparsers.add_parser('run', description='run template command',
            help='run template command')
    p_run.set_defaults(func=f_run)
    p_run.add_argument('-c', metavar='c-cmd',
            help='reduction shell command, e.g., "wc -l"')
    p_run.add_argument('-o', metavar='o-cmd', default='',
            help='shell command on output files')
    p_run.add_argument('-i', metavar='i-cmd', default='',
            help='shell command on input files')
    p_run.add_argument('-t', metavar='template', default=_get_default_template(),
            help='template name')
    p_run.add_argument('path', nargs='?', type=Path, default=Path.cwd(),
            help='folder to run commands on')
    p_run.add_argument('-y', action='store_true',
            help='run shell script without confirmation')

    p_tmpl = subparsers.add_parser('template', description='manage templates',
            help='manage templates')
    p_tmpl.set_defaults(func=f_tmpl)
    tmpl_cmds = p_tmpl.add_subparsers(dest='tmpl_cmd',
            help='additional help with sub-command -h')
    pg_ll = tmpl_cmds.add_parser('ll', description='List all templates')
    pg_ll.add_argument('tmpl',
                       nargs='?',
                       choices=utils.get_templates(),
                       help="template to show")
    pg_ls = tmpl_cmds.add_parser('ls', description='List all template names')
    pg_rm = tmpl_cmds.add_parser('rm', description='Remove template')
    pg_rm.add_argument('tmpl',
                       choices=utils.get_templates(),
                       help="template to delete")
    pg_set = tmpl_cmds.add_parser('set', description='Set template')
    pg_set.add_argument('tmpl',
                       choices=utils.get_templates(),
                       help="template to set")

    args = p.parse_args(argv)
    #print(args)

    if 'func' in args:  # sub commands
        args.func(args)
    else:
        p.print_help()  # pragma: no cover

if __name__ == '__main__':
    main()  # pragma: no cover

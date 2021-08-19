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
import shutil

from . import utils


def f_run(args):
    #print(args)
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
    #print(args)
    cmd = args.tmpl_cmd
    if not cmd:
        cmd = 'ls'
        tmpl = ''
    else:
        tmpl = args.tmpl
    if cmd == 'll':
        if tmpl:
            path = utils.get_tmpl_paths()[tmpl]
            print(utils.get_template(path).safe_substitute())
            sys.exit(0)
        for name, path in utils.get_tmpl_paths().items():
            print('='*5, name, '='*5)
            print(utils.get_template(path).safe_substitute())
    elif cmd == 'ls':
        if tmpl:  # show its path
            print(utils.get_tmpl_paths()[tmpl])
        else:     # show all template names
            print('\n'.join(sorted(utils.get_tmpl_paths().keys())))
    elif cmd == 'cp':
        config_dir = utils.get_config_dir()
        config_dir.mkdir(parents=True, exist_ok=True)
        from_name = utils.get_tmpl_paths()[tmpl]
        to_name = config_dir / (args.new_tmpl + '.tmpl')
        shutil.copy(from_name, to_name)
    elif cmd == 'add':
        # maybe trigger system EDITOR?
        print('type the template, end with CTRL+D:')
        s = sys.stdin.read()
        config_dir = utils.get_config_dir()
        config_dir.mkdir(parents=True, exist_ok=True)
        fname = config_dir / (tmpl + '.tmpl')
        with open(fname, 'w') as f:
            f.write(s)
    elif cmd == 'rm':
        templates = utils.get_tmpl_paths()
        for t in tmpl:
            templates[t].unlink()
    elif cmd == 'set':
        if tmpl is None:
            print(_get_default_template())
            sys.exit()
        config_dir = utils.get_config_dir()
        config_dir.mkdir(parents=True, exist_ok=True)
        ctx = utils.get_context()  # user defined template
        fname = config_dir / (tmpl + '.default')
        if ctx:
            ctx.rename(fname)
        else:
            open(fname, 'w').close()


def _get_default_template() -> str:
    """
    Return default template name
    """
    user_defined = utils.get_context()
    if user_defined is None:
        return 'for-loop'
    return user_defined.stem


def _template_name(name: str) -> str:
    """

    """
    existing = utils.get_tmpl_paths()
    if name in existing:
        print(f"Cannot use template name {name} since it already exists.")
        sys.exit(1)
    return name


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
    p_run.add_argument('-i', metavar='i-cmd', default='*',
            help='shell command on input files')
    p_run.add_argument('-t', metavar='template', default=_get_default_template(),
            help='template name; use default if not set explicitly')
    p_run.add_argument('path', nargs='?', type=Path, default=Path.cwd(),
            help='path to run commands on; use current path if omitted')
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
                       choices=utils.get_tmpl_paths(),
                       help="template to show")
    pg_ls = tmpl_cmds.add_parser('ls', description='List all template names')
    pg_ls.add_argument('tmpl',
                       nargs='?',
                       choices=utils.get_tmpl_paths(),
                       help="show template path")
    pg_cp = tmpl_cmds.add_parser('cp', description='Copy template')
    pg_cp.add_argument('tmpl',
                       choices=utils.get_tmpl_paths(),
                       help="template name to copy from")
    pg_cp.add_argument('new_tmpl',
                       type=_template_name,
                       help="template name to copy to")
    pg_add = tmpl_cmds.add_parser('add', description='Add template')
    pg_add.add_argument('tmpl',
                       type=_template_name,
                       help="template name to add")
    pg_rm = tmpl_cmds.add_parser('rm', description='Remove template')
    pg_rm.add_argument('tmpl',
                       nargs='+',
                       choices=utils.get_tmpl_paths(),
                       help="template(s) to delete")
    pg_set = tmpl_cmds.add_parser('set', description='Set template')
    pg_set.add_argument('tmpl',
                       nargs='?',
                       choices=utils.get_tmpl_paths(),
                       help="template to set")

    args = p.parse_args(argv)
    #print(args)

    if 'func' in args:  # sub commands
        args.func(args)
    else:
        p.print_help()  # pragma: no cover

if __name__ == '__main__':
    main()  # pragma: no cover

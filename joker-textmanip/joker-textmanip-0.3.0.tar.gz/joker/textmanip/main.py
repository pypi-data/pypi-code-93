#!/usr/bin/env python3
# coding: utf-8

import argparse
import sys
from pprint import pprint

from volkanic.cmdline import CommandRegistry


def _chkargs(args):
    if not args:
        return '-'
    if len(args) > 1:
        sys.exit('error: too many arguments')
    return args[0]


def _format_dict_as_shell_assoc_array(d, name):
    import os
    import shlex
    for k, v in d.items():
        if k.startswith('#'):
            continue
        v = os.path.expanduser(v)
        yield "{}[{}]={}".format(name, k, shlex.quote(v))


def parse_as_dict(prog, args):
    import argparse
    from joker.textmanip.tabular import textfile_to_dict
    desc = 'parse a text file into a dict and print'
    parser = argparse.ArgumentParser(prog=prog, description=desc)
    parser.add_argument('-i', '--invert', action='store_true')
    parser.add_argument('-a', '--shell-array')
    parser.add_argument('path', help='use "-" for stdin')
    ns = parser.parse_args(args)
    d = textfile_to_dict(ns.path, swap=ns.invert)
    if ns.shell_array:
        for line in _format_dict_as_shell_assoc_array(d, ns.shell_array):
            print(line, end=';')
    else:
        pprint(d, indent=4)
    print()


def quote_lines(prog=None, args=None):
    from joker.stream.shell import ShellStream
    desc = 'Quote each line of text'
    pr = argparse.ArgumentParser(prog=prog, description=desc)
    aa = pr.add_argument
    aa('-f', '--formula', default='QUOTED', help='e.g. -f "rm -fr QUOTED"')
    aa('path', metavar='PATH', help='use - to read from STDIN')
    ns = pr.parse_args(args)
    with ShellStream.open(ns.path) as sstm:
        for line in sstm.dense().quote(strip=True):
            print(line)


def pprint_list2d(_, args):
    from joker.textmanip.tabular import textfile_to_list
    textfile_to_list(_chkargs(args), printout=True)


def pprint_list(_, args):
    import pprint
    from joker.stream.shell import ShellStream
    lines = ShellStream.open(_chkargs(args)).dense()
    pprint.pprint(list(lines))


def vprint_tab(_, args):
    from joker.textmanip import tabular
    rows = tabular.textfile_to_list(_chkargs(args))
    for row in tabular.tabular_format(rows):
        print(*row)


def total(_, args):
    from joker.textmanip.tabular import textfile_numsum
    textfile_numsum(_chkargs(args), printout=True)


def grep(_, args):
    import re
    from joker.stream.shell import ShellStream
    try:
        pattern = args[0]
    except IndexError:
        return
    regex = re.compile(pattern)
    idx = 1 if regex.groups == 1 else 0
    with ShellStream.open(_chkargs(args[1:])) as sstm:
        for line in sstm.dense():
            mat = regex.search(line)
            if mat:
                print(mat.group(idx))


def _newline_conv(path, nl, suffix):
    with open(path) as fin, open(path + suffix, 'w', newline=nl) as fout:
        for line in fin:
            fout.write(line)


def nlconv(prog, args):
    desc = 'convert newlines'
    parser = argparse.ArgumentParser(prog=prog, description=desc)
    parser.add_argument('-s', '--style', choices=['n', 'rn', 'r'])
    parser.add_argument('path', help='an input data file')
    ns = parser.parse_args(args)
    newlines = {'n': '\n', 'rn': '\r\n', 'r': '\r'}
    suffix = '.{}.txt'.format(ns.style)
    _newline_conv(ns.path, newlines.get(ns.style), suffix)


entries = {
    'joker.textmanip.main:grep': '/',
    'joker.textmanip.main:total': '+',
    'joker.textmanip.main:nlconv': 'nl',
    'joker.textmanip.main:vprint_tab': 'tab',
    'joker.textmanip.main:pprint_list': 'l',
    'joker.textmanip.main:pprint_list2d': 'L',
    'joker.textmanip.main:parse_as_dict': 'd',
    'joker.textmanip.main:quote_lines': 'quote',
    'joker.textmanip.url:run_urlsim': 'urlsim',
    'joker.textmanip.draw:mkbox': 'box',
}

registry = CommandRegistry.from_entries(entries)

if __name__ == '__main__':
    registry()

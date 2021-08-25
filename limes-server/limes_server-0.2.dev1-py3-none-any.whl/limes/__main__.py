from .limes import Limes

import sys
from typing import List
from getpass import getpass
from functools import reduce

from .tools.qol import Switch, T
from .res import strings as Constants
from limes_common import config

def main(args:List[str] = sys.argv[1:]):
    # for later abstraction of help
    class Command:
        def __init__(self, schemas, options) -> None:
            self.schemas = schemas
            self.options = options

        def printHelp(self):
            self.printLine()
            print('Required:')

        def printLine(self):
            print('====================================================================')

    def Login():
        userKeys = ['-u', '--username']
        passKeys = ['-p', '--password']

        tries = 3
        user = input('Username: ')
        for _ in range(tries):
            try:
                password = getpass()
            except KeyboardInterrupt:
                return

            if limes.Login(user, password):
                return
        return '%s failed attempts, check your connection and credentials' % tries

    def _printHelp(unkownArg=False):
        msg = 'use [-h] or [--help] to view options\nor view available documentation at https://github.com/Tony-xy-Liu/Limes/'
        if unkownArg:
            msg = '[%s] was not recognized\n%s' % (unkownArg, msg)
        return msg

    def _getVal(keys: List[str], args: List[str]) -> tuple[bool, str]:
        next = 1
        for item in args:
            if item in keys and next < len(args):
                return True, args[next]
            next +=1
        return False, ""

    limes = Limes()
    arg = args[0] if len(args) > 0 else ''

    def base():
        print(Constants.version)
        limes._auth()

    # the switch doesn't need to be fast, make it easier to make
    # also need to add hints here
    return Switch(arg, {
        '': base,
        '-h': lambda: Constants.help,
        '--help': lambda: Constants.help,
        'login': Login,
        'dlogin': lambda: limes.dLogin(),
        # 'search': Search,
        # 'blast': Blast,
        # 'add': Add,
    }, lambda: _printHelp(arg))

if __name__ == "__main__":
    args = sys.argv[1:]
    a = args[0] if len(args) > 0 else ''
    try:
        end = main()
    except KeyboardInterrupt:
        print('KeyboardInterrupt')
        end = None
    if not end is None and end != '':
        sys.exit(end)
    else:
        sys.exit()
# Copyright 2020, castLabs GmbH

from .. import __version__
from ..core.failure import die
from ..account import Account
from argparse import ArgumentParser
from sys import argv
from os import environ, path

################################################################################

def main():
  try:
    bp = ArgumentParser(path.basename(argv[0]))
    bp.add_argument('-v', '--version', action='version', version='%(prog)s {}'.format(__version__))
    bp.add_argument('-n', '--no-ask', help='enable non-interactive mode',
      action='store_true', default='EVS_NO_ASK' in environ,
    )

    _cred = ArgumentParser(add_help=False)
    _cred.add_argument('-A', '--account-name', help='provide account name [CACHED]',
      default=environ.get('EVS_ACCOUNT_NAME')
    )
    _cred.add_argument('-P', '--passwd', help='provide account password',
      default=environ.get('EVS_PASSWD')
    )
    _email = ArgumentParser(add_help=False)
    _email.add_argument('-E', '--email', help='provide email address [CACHED]',
      default=environ.get('EVS_EMAIL')
    )
    _details = ArgumentParser(add_help=False)
    _details.add_argument('-F', '--first-name', help='provide first name [CACHED]',
      default=environ.get('EVS_FIRST_NAME')
    )
    _details.add_argument('-L', '--last-name', help='provide last name [CACHED]',
      default=environ.get('EVS_LAST_NAME')
    )
    _details.add_argument('-O', '--organization', help='provide organization [CACHED]',
      default=environ.get('EVS_ORGANIZATION')
    )
    _no_confirm = ArgumentParser(add_help=False)
    _no_confirm.add_argument('-N', '--no-confirm', help='don\'t automatically ask for confirmation',
      default=environ.get('EVS_NO_CONFIRM')
    )
    _code = ArgumentParser(add_help=False)
    _code.add_argument('-C', '--code', help='provide confirmation code',
      default=environ.get('EVS_CODE')
    )

    sp = bp.add_subparsers(title='commands', dest='command', required=True)
    cp = sp.add_parser('signup', help='sign up for EVS account',
      aliases=['sup'],
      parents=[_cred, _email, _details, _no_confirm]
    )
    cp.set_defaults(command=Account.signup)
    cp = sp.add_parser('resend', help='resend EVS account confirmation code',
      aliases=['rs'],
      parents=[_cred, _no_confirm]
    )
    cp.set_defaults(command=Account.resend)
    cp = sp.add_parser('confirm-signup', help='confirm account signup',
      aliases=['csup'],
      parents=[_cred, _code]
    )
    cp.set_defaults(command=Account.confirm_signup)
    cp = sp.add_parser('update', help='update account details',
      aliases=['up'],
      parents=[_cred, _details]
    )
    cp.set_defaults(command=Account.update)
    cp = sp.add_parser('reset', help='reset account password',
      aliases=['res'],
      parents=[_cred, _no_confirm]
    )
    cp.set_defaults(command=Account.reset)
    cp = sp.add_parser('confirm-reset', help='confirm account password reset',
      aliases=['cres'],
      parents=[_cred, _code]
    )
    cp.set_defaults(command=Account.confirm_reset)
    cp = sp.add_parser('refresh', help='refresh authorization tokens',
      aliases=['r'],
      parents=[_cred]
    )
    cp.set_defaults(command=Account.refresh)
    cp = sp.add_parser('deauth', help='discard any authorization tokens',
      aliases=['da'],
      parents=[]
    )
    cp.set_defaults(command=Account.deauth)
    cp = sp.add_parser('reauth', help='discard any authorization tokens & refresh',
      aliases=['ra'],
      parents=[_cred]
    )
    cp.set_defaults(command=Account.reauth)
    cp = sp.add_parser('delete', help='delete EVS account',
      aliases=['del'],
      parents=[_cred]
    )
    cp.set_defaults(command=Account.delete)

    args = vars(bp.parse_args())
    account = Account(no_ask=args.pop('no_ask'))
    run = args.pop('command')
    run(account, **args)
  except (Exception, KeyboardInterrupt) as e:
    die(e)

################################################################################

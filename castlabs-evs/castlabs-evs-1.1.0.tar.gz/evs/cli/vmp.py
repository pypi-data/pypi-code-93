# Copyright 2020, castLabs GmbH

from .. import __version__
from ..core.failure import die
from ..vmp import VMP
from argparse import ArgumentParser
from sys import argv
from os import environ, path

################################################################################

def main():
  try:
    bp = ArgumentParser(path.basename(argv[0]))
    bp.add_argument('-v', '--version', action='version', version='%(prog)s {}'.format(__version__))
    bp.add_argument('-n', '--no-ask', help='enable non-interactive mode',
      action='store_true', default='EVS_NO_ASK' in environ
    )
    bp.add_argument('-a', '--any-ski', help='verify any subject key identifier',
      action='store_true', default='EVS_ANY_SKI' in environ
    )

    _kind = ArgumentParser(add_help=False)
    _kind.set_defaults(kind=environ.get('EVS_KIND', 'streaming'))
    _kind.add_argument('-s', '--streaming', help='streaming only signature (default)',
      dest='kind', action='store_const', const='streaming'
    )
    _kind.add_argument('-p', '--persistent', help='streaming and persistent download signature',
      dest='kind', action='store_const', const='persistent'
    )
    _flags = ArgumentParser(add_help=False)
    _flags.add_argument('-i', '--intermediate', help='generate intermediate signature',
      dest='intermediate', action='store_true', default='EVS_INTERMEDIATE' in environ
    )
    _min_days = ArgumentParser(add_help=False)
    _min_days.add_argument('-M', '--min-days', help='minimum number of remaining valid days',
      type=int, default=environ.get('EVS_MIN_DAYS', 90)
    )
    _force = ArgumentParser(add_help=False)
    _force.add_argument('-f', '--force', help='force new signature',
      action='store_true', default='EVS_FORCE' in environ
    )
    _gz = ArgumentParser(add_help=False)
    _gz.add_argument('-z', '--gz', help='request gzip upload (slower for fast connections)',
      action='store_true', default='EVS_GZ' in environ
    )
    _cred = ArgumentParser(add_help=False)
    _cred.add_argument('-A', '--account-name', help='provide account name [CACHED]',
      default=environ.get('EVS_ACCOUNT_NAME')
    )
    _cred.add_argument('-P', '--passwd', help='provide account password',
      default=environ.get('EVS_PASSWD')
    )

    _name_hint = ArgumentParser(add_help=False)
    _name_hint.add_argument('-H', '--name-hint', help='provide name hint',
      default=environ.get('EVS_NAME_HINT')
    )

    _assets = ArgumentParser(add_help=False)
    _assets.add_argument('bin', help='path to binary')
    _assets.add_argument('sig', help='path to signature', nargs='?')
    _pkgs = ArgumentParser(add_help=False)
    _pkgs.add_argument('pkg', help='path to electron package directory', nargs='+')

    sp = bp.add_subparsers(title='commands', dest='command', required=True)
    cp = sp.add_parser('verify', help='verify signature',
      aliases=['v'],
      parents=[_kind, _flags, _min_days, _assets]
    )
    cp.set_defaults(command=VMP.verify)
    cp = sp.add_parser('sign', help='refresh signature',
      aliases=['s'],
      parents=[_kind, _flags, _min_days, _force, _gz, _cred, _assets]
    )
    cp.set_defaults(command=VMP.sign)
    cp = sp.add_parser('verify-pkg', help='verify electron package signature',
      aliases=['vp'],
      parents=[_kind, _name_hint, _min_days, _pkgs]
    )
    cp.set_defaults(command=VMP.verify_pkg)
    cp = sp.add_parser('sign-pkg', help='refresh electron package signature',
      aliases=['sp'],
      parents=[_kind, _name_hint, _min_days, _force, _gz, _cred, _pkgs]
    )
    cp.set_defaults(command=VMP.sign_pkg)

    args = vars(bp.parse_args())
    vmp = VMP(no_ask=args.pop('no_ask'), any_ski=args.pop('any_ski'))
    run = args.pop('command')
    run(vmp, **args)
  except (Exception, KeyboardInterrupt) as e:
    die(e)

################################################################################

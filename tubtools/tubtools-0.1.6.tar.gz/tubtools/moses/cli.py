import argparse

from .people import main as main_ppl

description_ppl = '''Search for people in the MOSES system based on different attributes.'''


def setup_parser_ppl(parser_ppl: argparse.ArgumentParser):
    parser_ppl.set_defaults(func=main_ppl)
    parser_ppl.add_argument('-u', '--user')
    parser_ppl.add_argument('-p', '--password')

    parser_ppl.add_argument('-n', '--firstname')
    parser_ppl.add_argument('-s', '--surname')
    parser_ppl.add_argument('-e', '--email')
    parser_ppl.add_argument('-i', '--id')
    parser_ppl.add_argument('-a', '--account-name')

    parser_ppl.add_argument('-b', '--batch', choices=['email', 'id', 'account'],
                            help='Read a batch of emails/student ids/account names from stdin and fill-in the details.')

    parser_ppl.add_argument('--extended', help='Get extra information such as email and field of study.'
                                               'Requires second query for each result.',
                            action='store_true')

    creds_group = parser_ppl.add_mutually_exclusive_group()
    creds_group.add_argument('--store-credentials',
                             help='Stores credentials for the given user in the default keyring backend.',
                             action='store_true')
    creds_group.add_argument('--clear-credentials',
                             help='Deletes any stored credentials for the given user.',
                             action='store_true')


def main():
    description = 'Scraping tools for the TU Berlin Moses platform.'

    parser = argparse.ArgumentParser(prog='moses', description=description)
    subparsers = parser.add_subparsers(help='Available subcommands', dest='subcommand')

    parser_ppl = subparsers.add_parser('people', aliases=['ppl'], description=description_ppl)
    setup_parser_ppl(parser_ppl)

    args = parser.parse_args()

    if args.subcommand is None:
        parser.print_usage()
        return

    args.func(args)


if __name__ == '__main__':
    main()

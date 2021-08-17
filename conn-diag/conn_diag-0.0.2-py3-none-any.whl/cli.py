import sys
import getpass
import argparse

from conn_diag.conn_diag.core import dumps_cmd
from conn_diag.conn_diag.core import check_connectivity

from conn_diag.conn_diag.utilities import is_valid_file
from conn_diag.conn_diag.constants import DEFAULT_SSH_TIMEOUT
from conn_diag.conn_diag.constants import DEFAULT_CHECK_TIMEOUT

from conn_diag.conn_parser.dumps import dumps_connections
from conn_diag.conn_parser.parse import parse_connections_from_str
from conn_diag.conn_parser.parse import parse_connections_from_file


class MyParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('%s: error: %s\n' % (self.prog, message))
        sys.exit(2)


def create_parser():
    parser = argparse.ArgumentParser(prog='conn-diag')

    # positional
    parser.add_argument('conn', nargs='?', default=None)

    # options
    parser.add_argument('-d', '--delimiter', default='#', metavar='', help='Set delimiter in connection')
    parser.add_argument('-l', '--line-sep', dest='line_separator', metavar='', default='\n', help='Set line separator between connections')
    parser.add_argument('-v', '--verbose', action='store_true', help='Print more details')
    parser.add_argument('--ssh-timeout', metavar='', type=int, choices=range(1, 11), default=DEFAULT_SSH_TIMEOUT, help='Set timeout for ssh connection')
    parser.add_argument('--check-timeout', metavar='', type=int, choices=range(1, 11), default=DEFAULT_CHECK_TIMEOUT, help='Set timeout for check connectivity')
    parser.add_argument('--parallel', action='store_true', help='Check connectivity in parallel')
    parser.add_argument('--cidr', action='store_true', help='Unrange subnet IP')
    parser.add_argument('--range', action='store_true', help='Range connectivity')
    parser.add_argument('--unrange', action='store_true', help='Unrange connectivity')
    parser.add_argument('--short', action='store_true', help='Shorten ranged connectivity by combining common subnet IPs with ";"')
    parser.add_argument('--from-file', metavar='', type=lambda x: is_valid_file(parser, x), help='get connections from file',)

    # SSH credentials
    parser.add_argument('--ssh-username', dest='ssh_username', metavar='', help='ssh username')
    parser.add_argument('--ssh-key', dest='ssh_key', metavar='', help='ssh key', type=lambda x: is_valid_file(parser, x))

    # output actions
    action_group = parser.add_mutually_exclusive_group()
    action_group.add_argument('--check', action='store_true', help='Check connectivity')
    action_group.add_argument('--dump-cmd', action='store_true', help='Dump commends that will run on remote hosts')

    return parser


def parse_args(args):
    parser = create_parser()
    args = parser.parse_args(args)

    if not args.range and args.short:
        raise parser.error(message='--range is required for --short')

    #
    # LOAD CONNECTIONS
    #

    if args.conn is not None:
        connections = parse_connections_from_str(_str=args.conn, delimiter=args.delimiter, line_separator=args.line_separator)
    elif args.from_file is not None:
        connections = parse_connections_from_file(file=args.from_file, delimiter=args.delimiter, line_separator=args.line_separator)
    else:
        raise parser.error(message='required [conn | --from-file]')

    #
    # ACTIONS
    #

    if args.check:
        if all('127.0.0.1' == conn.source for conn in connections):
            ssh_username = None
            ssh_password = None
            ssh_key = None
        else:
            ssh_username = args.ssh_username or input('ssh username: ')
            ssh_password = args.ssh_key or getpass.getpass(prompt='ssh password: ')
            ssh_key = args.ssh_key

        ssh_result_col = check_connectivity(connections=connections,
                                            check_timeout=args.check_timeout,
                                            verbose=args.verbose,
                                            parallel=args.parallel,
                                            ssh_timeout=args.ssh_timeout,
                                            ssh_username=ssh_username,
                                            ssh_password=ssh_password,
                                            ssh_key=ssh_key)

        ssh_result_col.print_table(_range=args.range, short=args.short)
    elif args.dump_cmd:
        result = dumps_cmd(connections=connections, check_timeout=args.check_timeout)
        print(result)
    else:
        connections_str = dumps_connections(connections=connections,
                                            _range=args.range,
                                            unrange=args.unrange,
                                            short=args.short,
                                            delimiter=args.delimiter,
                                            line_separator=args.line_separator,
                                            cidr=args.cidr)
        print(connections_str)

import sys
import traceback
from conn_diag.cli import parse_args
from conn_diag.conn_diag.exceptions import ConnDiagError
from conn_diag.conn_parser.exceptions import ConnParserError


def print_exception(e):
    print('{}: {}'.format(e.__class__.__name__, str(e)))


def print_traceback():
    print('UncaughtError')
    print(traceback.format_exc())


def main():
    try:
        parse_args(sys.argv[1:])
        return 0
    except KeyboardInterrupt:
        print('\nYou have interrupted the program.')
        return 1
    except ConnParserError as e:
        print_exception(e)
        return 1
    except ConnDiagError as e:
        print_exception(e)
        return 1
    except Exception as e:
        print_exception(e)
        return 1


if __name__ == '__main__':
    sys.exit(main())

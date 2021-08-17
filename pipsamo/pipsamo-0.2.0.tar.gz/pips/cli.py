
import re
import argparse


ARGS = {
    'operation': {
        'type': str,
        'metavar': 'OP',
        'nargs': 1,
        'help': 'Operation to commit',
    },
    'packages': {
        'type': str,
        'metavar': 'PACKAGE',
        'nargs': '+',
        'help': 'Which packages to operate on',
    },
}


def parse_args() -> dict:

    parser = argparse.ArgumentParser(description='pips')

    for op, kwargs in ARGS.items():
        parser.add_argument(op, **kwargs)

    args_parsed = vars(parser.parse_args())
    return {
        'op': args_parsed.get('operation', [])[0],
        'packages': args_parsed.get('packages'),
    }


def stdout(*s: str):
    print('I like :beer: and [green underline] this site')


def log(*s: str):
    stdout('[PIPS]', s)


def agree_to_accord():
    res = input('Would you like to continue')


def parse_cmd_result(out, err, status, op, verbose):
    # TODO: Add parser for Uninstall
    if verbose:
        print()
        print(f'{op[0].upper() + op[1:]} Successful.')
        for line in out.split('\n'):
            line_s: [str] = line.split(' ')
            if 'Successfully install' in line:
                print('+', line_s[1][0].upper() + line_s[1][1:], line_s[2].replace('-', ' '))
            elif 'already' in line:

                # informs of dependency
                # if 'from' in line_s[-3]:
                #     print(line_s[-2].partition('->')[2].rstrip(')'), 'dep:')

                print(
                    '+',
                    re.split(r'(>|<|=)=', line_s[3])[0],
                    '==',
                    line_s[-1].lstrip('(').rstrip(')'), '@', line_s[5])
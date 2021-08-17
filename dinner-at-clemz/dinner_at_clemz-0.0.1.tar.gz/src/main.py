import argparse
from argparse import ArgumentParser
from argparse import ArgumentDefaultsHelpFormatter
from . import messages


def argparser():
    parser = ArgumentParser(
        formatter_class=ArgumentDefaultsHelpFormatter,
        add_help=False
    )
    parser.add_argument("--name", "-n", default=None, required=False, 
                        help="Display the message from the given names",
                        nargs='+',
                        choices=[x.lower() for x in messages.__all__])
    parser.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS)
    return parser


def main():
    args = argparser().parse_args()
    names = args.name
    all_messages = {name.lower(): messages.__dict__.get(name) for name in messages.__all__}
    if names is None:
        for _, tomodachi in all_messages.items():
            tomodachi().show_message()
    else:
        for name in names:
            all_messages[name]().show_message()


if __name__ == '__main__':
    main()

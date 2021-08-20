import argparse
import logging
from pathlib import Path

from .utils import (
    run_scraper,
    generate_rule,
    create_template
)

FORMAT = 'PWBM DevTools: %(message)s'
logging.basicConfig(level=logging.INFO, format=FORMAT)


def _script_param(param: str):
    name, value = param.split('=', maxsplit=1)
    return {name.strip(): value}


def _boilerplate_path(path: str):
    path = Path(path).absolute()
    if path.exists():
        raise argparse.ArgumentError(None, f'Path already exists: {path}')
    for parent_path in path.parents:
        if parent_path.is_file():
            raise argparse.ArgumentError(None, f'Path is a file but is treated as a directory: {parent_path}')
    return path


def _script_path(path: str):
    path = Path(path).absolute()
    if not (path.exists() and path.is_file()):
        raise argparse.ArgumentError(None, 'No such file: {path}')
    return path


def _output_path(path: str):
    path = Path(path).absolute()
    if path.exists() and not path.is_dir():
        raise argparse.ArgumentError(None, f'Path is not a directory: {path}')
    for parent_path in path.parents:
        if parent_path.is_file():
            raise argparse.ArgumentError(None, f'Path is a file but is treated as a directory: {parent_path}')
    return path


def _get_parser():
    parser = argparse.ArgumentParser(description='PWBM Scraping PLatform local development tools')
    subparsers = parser.add_subparsers(title='Commands')

    parser_boilerplate = subparsers.add_parser(
        name="boilerplate",
        description='Create custom scraper boilerplate script',
        help='Create custom scraper boilerplate script',
    )
    parser_boilerplate.set_defaults(func=create_template)
    parser_boilerplate.add_argument(
        'output', type=_boilerplate_path, nargs='?', default='scraper.py',
        help='Path to the file/directory to save the boilerplate script. Default: %(default)s',
    )

    parser_run = subparsers.add_parser(
        name="run",
        description='Run custom scraper script',
        help='Run custom scraper script',
    )
    parser_run.set_defaults(func=run_scraper)
    parser_run.add_argument(
        'input', type=_script_path,
        help='Path to the custom python script to run',
    )
    parser_run.add_argument(
        '-p', '--params', metavar='SCRIPT_PARAM', type=_script_param, nargs='+', default={},
        help='Additional scraper script params in a form of <name>=<value>',
    )
    parser_run.add_argument(
        '-o', '--output', type=_output_path, default='.',
        help='Directory to store execution results. Default: %(default)s'
    )

    parser_wrap = subparsers.add_parser(
        name="wrap",
        description='Wrap custom scraper script into a SP pipeline definition',
        help='Wrap custom scraper script into a SP pipeline definition',
    )
    parser_wrap.set_defaults(func=generate_rule)
    parser_wrap.add_argument(
        'input', type=argparse.FileType('r'),
        help='Path to the custom python script to wrap',
    )
    parser_wrap.add_argument(
        '-p', '--params', metavar='SCRIPT_PARAM', type=_script_param, nargs='+', default={},
        help='Additional scraper script params in a form of <name>=<value>'
    )
    parser_wrap.add_argument(
        '-o', '--output', type=argparse.FileType('w'), default='-',
        help='Path to the output file to save the resulting rule. Will use stdout if omitted',
    )

    return parser


def main():
    parser = _get_parser()
    args = parser.parse_args()
    try:
        args.func(args)
    except AttributeError:
        parser.print_help()


if __name__ == '__main__':
    main()

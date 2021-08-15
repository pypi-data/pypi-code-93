# !/usr/bin/env python3
# coding: utf-8
import argparse
from venv import EnvBuilder

from ienv.settings import *


def get_parser():
    _ = argparse.ArgumentParser(description=DESCRIPTION, epilog=f'Source: {URL}')

    _.add_argument('--project_dir', '-p', help='Directory of project, defaults to the current folder.')
    _.add_argument('--env_dir', '-e', help='Parent directory of env, '
                                           'defined by the environment variable "IENV", '
                                           f'which defaults to be "{DEFAULT}".')
    return _


def get_env_dir(project_dir: Path = None):
    return Path(IENV) / project_dir.drive[:-1] / project_dir.as_posix()[len(project_dir.anchor):]


def main():
    parser = get_parser()
    args = parser.parse_args()

    env_dir = args.env_dir or get_env_dir(args.project_dir or Path().absolute())
    print('venv:', env_dir.absolute().as_posix().replace('/', '\\'), end='\n\n')

    if env_dir.exists():
        activate = (env_dir / binname / 'activate.bat').as_posix()
        print('activate:', activate.replace('/', '\\'))
    else:
        env_builder = EnvBuilder(with_pip=True, upgrade_deps=True)
        env_builder.create(env_dir=env_dir)


if __name__ == '__main__':
    main()

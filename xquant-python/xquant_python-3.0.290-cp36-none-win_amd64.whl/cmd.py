from os import path, getcwd, getenv, system
from shutil import rmtree
from typing import Any, Optional

import click
import sys

from . import global_config
from .global_config import *
from .utils import expand_path, create_dir_if_not_exist


def is_first_start() -> bool:
    """Detects first app start."""
    return not path.isdir(global_config.config_dir)


def is_cwd_exist() -> bool:
    """Checks cwd existence"""
    try:
        getcwd()
        return True
    except FileNotFoundError:
        return False


def init_config_dir() -> None:
    """Initializes global config directory."""
    # pylint: disable=W0703
    try:
        create_dir_if_not_exist(config_dir)
        init_cache_dir()
    except Exception as exception:
        print(f'Error during initialization: {str(exception)}, cleanup ...')
        rmtree(config_dir)
        sys.exit(1)


def init_cache_dir() -> None:
    """Initialize download cache dir"""
    create_dir_if_not_exist(get_download_cache_dir())


@click.group(invoke_without_command=True)
@click.pass_context
@click.version_option(package_name='xquant-python')
@click.option('--config-directory', type=click.Path(),
              default=global_config.config_dir,
              help='Path to configuration directory')
@click.option('--cache-directory', type=click.Path(),
              default='',
              help='Path to download cache directory')
def xquant_cmd(ctx: Any, config_directory: str, cache_directory: str) -> None:
    """
    This script helps to run xQuant
    """

    if not is_cwd_exist():
        it = getenv('PWD', 'it')  # pylint: disable=invalid-name
        print(f'Could not determine current working directory. Does {it} exist? Exiting...')
        sys.exit(1)

    global_config.config_dir = expand_path(config_directory)

    if cache_directory:
        global_config.cache_dir = expand_path(cache_directory)

    if is_first_start():
        init_config_dir()
        click.echo(ctx.get_help())
    elif not ctx.invoked_subcommand:
        click.echo(ctx.get_help())
    else:
        init_cache_dir()


@click.command(short_help='执行xQuant策略代码')
@click.argument('executable', type=click.STRING, required=False)
@click.option('--config', type=click.Path(),
              default=global_config.config_file,
              help='config位置')
@click.option('--user', type=click.STRING,
              help='用户id')
@click.option('--token', type=click.STRING,
              help='用户token')
def run(executable: Optional[str], config: str, user: str, token: str) -> None:
    """xQuant运行可执行的文件(strategy.py/so/dll)"""
    if executable[-3:] == '.py':
        system(f'{sys.executable} {executable} --config={config} --user={user} --token={token}')
    elif executable[-3:] == '.so' or executable[-4:] == '.dll' or executable[-6:] == '.dylib':
        import xquant
        import pathlib
        xquant_dir = pathlib.Path(xquant.__file__).resolve().parent
        print(xquant_dir)
        system(f'{xquant_dir}/commands/xquant_cli -u {user} -p {token} -s {executable} -c {config}')
    else:
        print(f'未知的可执行文件: {executable}')


xquant_cmd.add_command(run, name='run')

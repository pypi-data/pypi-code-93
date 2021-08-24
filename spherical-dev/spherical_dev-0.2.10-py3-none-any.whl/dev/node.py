import functools
import os
import pathlib
import shutil
from collections.abc import Mapping

import invoke


@invoke.task
def node_install(ctx):
    """
    Install node and npm in current virtual env if
    the node env is not installed
    """
    active_venv = os.environ.get('VIRTUAL_ENV', None)

    if not active_venv:
        return

    which = functools.partial(
        shutil.which,
        path=pathlib.Path(active_venv) / 'bin',
    )
    shim_path = which('shim')
    nodeenv_path = which('nodeenv')

    # if python virtual env is active (active_venv)
    # and nodeenv package is installed (nodeenv_path),
    # but nodeenv is not initialized in active virtual env (shim_path)
    # (not relevant for github actions because virtual env is absent)
    if nodeenv_path and not shim_path:
        ctx.run('nodeenv -p')


@invoke.task(node_install, iterable=['packages'])
def npm_install(ctx, packages=None):
    if isinstance(packages, Mapping):
        packages = [
            f'{package}{("@" + version) if version else ""}'
            for package, version in packages.items()
        ]
    packages = ('-g', *packages) if packages else ()
    ctx.run(' '.join(('npm', 'install', '--no-save', *packages)))


@invoke.task(node_install)
def mocha_test(
    ctx,
    path,
    packages={},
    esm=True,
    watch=False,
    debug=False,
    grep='',
    timeout=10000,
):
    packages.setdefault('mocha', '')
    if esm:
        packages.setdefault('esm', '')
    npm_install(ctx, packages=packages)

    node_path = ctx.run('npm root --quiet -g', hide=True).stdout.strip()
    grep = f' -- -grep "{grep}"' if grep else ''
    ctx.run(
        (
            'mocha -c '
            f'{"-r esm" if esm else ""} '
            f'{"-w" if watch else ""} '
            f'{"--inspect-brk" if debug else "--full-trace"} '
            f'--timeout {timeout} '
            f'{path} '
            f'{grep}'
        ),
        env={'NODE_PATH': node_path},
    )

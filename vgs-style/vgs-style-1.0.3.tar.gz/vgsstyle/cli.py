import sys
from pathlib import Path
from typing import List

import click
import pkg_resources

from .config import InvalidConfigException, load_config
from .linters.base import Linter
from .linters.black import BlackLinter
from .linters.flake import Flake8Linter


LINTERS: List[Linter] = [Flake8Linter, BlackLinter]


@click.group()
@click.pass_context
def main(ctx: click.Context):
    ctx.ensure_object(dict)
    try:
        ctx.obj["config"] = load_config()
    except InvalidConfigException as exc:
        click.echo(f"Invalid config: {exc}", err=True)
        ctx.exit(1)


@main.command()
@click.pass_context
@click.argument("paths", nargs=-1, type=click.Path(exists=True))
def lint(ctx: click.Context, paths: List[str] = None) -> None:
    ok = True

    if not paths:
        paths = [Path.cwd()]

    for linter_cls in LINTERS:
        linter = linter_cls(ctx.obj["config"])
        for error in linter.run(paths):
            if ok:
                ok = False
            click.echo(f"[{linter.name}] {error}", err=True)

    if not ok:
        sys.exit(1)


@main.command()
@click.pass_context
@click.argument("paths", nargs=-1, type=click.Path(exists=True))
def format(ctx: click.Context, paths: List[str] = None) -> None:
    black = BlackLinter(config=ctx.obj["config"])
    black.format(paths)


@main.command()
@click.pass_context
@click.argument("dst", type=click.Path(exists=True, file_okay=False, writable=True))
def dump_configs(ctx: click.Context, dst: str) -> None:
    dst = Path(dst)
    for linter_cls in LINTERS:
        linter_cls(ctx.obj["config"]).dump_config(dst)


@main.command()
def version():
    click.echo(pkg_resources.get_distribution("vgs-style").version)


if __name__ == "__main__":
    main()

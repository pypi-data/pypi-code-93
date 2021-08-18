import pathlib

import click

from tktl.cli.common import ClickCommand
from tktl.commands.lazify import lazify_file
from tktl.core.config import settings


@click.command(
    "lazify",
    help="Add metadata to parquet file for lazy loading",
    cls=ClickCommand,
    **settings.HELP_COLORS_DICT,
)
@click.argument("source_path")
@click.argument("target_path")
@click.pass_context
def lazify(ctx, source_path: str, target_path: str):

    source_pathlib_path = pathlib.Path(source_path)
    target_pathlib_path = pathlib.Path(target_path)

    if not source_pathlib_path.is_file():
        raise click.BadParameter(
            f"'{source_path}' does not exist or is not a file", param_hint="source_path"
        )
    if source_pathlib_path.suffix != ".pqt":
        raise click.BadParameter(
            f"'{source_path}' does not seem to be a parquet file",
            param_hint="source_path",
        )

    lazify_file(
        source_path=source_pathlib_path, target_path=target_pathlib_path, data=None
    )

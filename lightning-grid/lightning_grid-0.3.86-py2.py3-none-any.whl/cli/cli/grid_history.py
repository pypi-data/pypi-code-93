from typing import Optional

import click

from grid.cli import rich_click
from grid.cli.client import Grid


@click.option(
    '--global',
    'is_global',
    type=bool,
    is_flag=True,
    help='Fetch history from everyone in the team when flag is passed'
)
@rich_click.command()
def history(is_global: Optional[bool] = False) -> None:
    """View list of historic Runs."""
    client = Grid()
    client.history(is_global=is_global)

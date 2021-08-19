from typing import Optional

import click

from grid.cli import rich_click
from grid.cli.client import Grid
import grid.cli.globals as env
from grid.cli.types import ObservableType
from grid.cli.utilities import is_experiment


def _check_is_experiment(ctx, _param, value):
    """Callback that checks if a value is an experiment."""
    if not value:
        return value

    if is_experiment(value):
        raise click.BadArgumentUsage(f"Must pass a Run name, not Experiment: {value}")

    return value


@rich_click.command()
@rich_click.argument('run', type=str, nargs=1, required=False, callback=_check_is_experiment)
@click.option('--details', type=bool, help='Shows Run submission details', is_flag=True)
@click.option(
    '--export',
    type=click.Choice(['csv', 'json'], case_sensitive=False),
    help='Exports status output to supplied file type'
)
@click.option(
    '--global', 'is_global', type=bool, is_flag=True, help='Fetch status from all collaborators when flag is passed'
)
def status(
    run: Optional[str] = None,
    details: Optional[bool] = False,
    export: Optional[str] = None,
    is_global: Optional[bool] = False
) -> None:
    """Checks the status of Runs, Experiments, and Sessions."""
    client = Grid()

    # Setup global flag to show build errors with
    # Runs or Experiments. This is more effective than
    # passing the flag around through all the invocations.
    env.SHOW_PROCESS_STATUS_DETAILS = details

    # Users can see the statuses of Experiments
    # by selecting runs.
    kind = ObservableType.RUN
    observable = []
    if run:
        observable = [run]
        kind = ObservableType.EXPERIMENT

    client.status(kind=kind, identifiers=observable, export=export, is_global=is_global)

    # If we have a Run, then don't print the global
    # interactive nodes table.
    if not run:
        client.status(kind=ObservableType.INTERACTIVE, identifiers=observable, export=export, is_global=is_global)

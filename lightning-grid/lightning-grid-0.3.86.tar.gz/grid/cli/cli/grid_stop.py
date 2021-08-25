from typing import List

import click

from grid.cli import rich_click
from grid.cli.client import Grid
from grid.cli.utilities import is_experiment


@rich_click.group()
def stop():
    """Stop Runs, Experiments, or Sessions."""
    pass


@stop.command()
@rich_click.argument('experiment_ids', type=str, required=True, nargs=-1, help="The experiment IDs to stop.")
def experiment(experiment_ids: List[str]):
    """Stop one or more experiments."""
    client = Grid()
    for experiment in experiment_ids:
        if is_experiment(experiment):
            client.cancel(experiment_name=experiment)
        else:
            raise click.ClickException(f"Could not find experiment: {experiment}.")


@stop.command()
@rich_click.argument('run_ids', type=str, required=True, nargs=-1, help="The run IDs to stop.")
def run(run_ids: List[str]):
    """Stop one or more runs."""
    client = Grid()
    for run in run_ids:
        if client.is_run(run_name=run):
            client.cancel(run_name=run)
        else:
            raise click.ClickException(f"Could not find run: {run}.")


@stop.command()
@rich_click.argument('session_ids', type=str, required=True, nargs=-1, help="The session IDs to stop.")
def session(session_ids: List[str]):
    """Stop one or more sessions."""
    client = Grid()
    for session in session_ids:
        if client.is_interactive_node(interactive_node_name=session):
            client.delete_interactive_node(interactive_node_name=session)
        else:
            raise click.ClickException(f"Could not find session: {session}.")

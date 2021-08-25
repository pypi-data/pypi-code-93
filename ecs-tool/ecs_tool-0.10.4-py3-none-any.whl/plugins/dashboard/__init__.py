import click

from .app import EcsToolApp


@click.command(name="dashboard")
def cli():
    """
    Dashboard
    """
    EcsToolApp.run(log="textual.log")

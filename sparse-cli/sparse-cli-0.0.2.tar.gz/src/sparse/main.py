"""Sparse command line utility.

  Run `sparse --help` for usage.
"""

import click

from .resources.auth import auth
# from .resources.account import account
# from .resources.database import database

from . import browser
from . import config

@click.group(cls=click.Group)
@click.option('--endpoint', metavar='URL', envvar='SPARSE_ENDPOINT',
              default=config.default_endpoint(), show_default=True,
              help='Web service API endpoint.')
@click.pass_context
def cli(ctx, endpoint):
    """Sparse - Low latency database hosting."""

    ctx.obj = NotImplemented

@cli.command()
@click.pass_obj
def docs(obj):
    """Open the online documentation in a web browser."""

    browser.open(config.documentation_url())

cli.add_command(auth)
# cli.add_command(account)
# cli.add_command(database)

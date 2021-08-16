#!/usr/bin/env python

import click
import logging
import nextcodecli

log = logging.getLogger(__name__)


@click.command()
@click.pass_context
def cli(ctx):
    """
    Show the Nextcode CLI version.
    """
    click.echo(nextcodecli.get_version_string())

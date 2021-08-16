#!/usr/bin/env python

import click

from nextcodecli.utils import check_profile


@click.group()
@click.pass_context
def cli(ctx):
    """Root subcommand for pipelines functionality"""
    if ctx.obj.service is None:
        check_profile(ctx)
        ctx.obj.service = ctx.obj.client.service("pipelines")
        ctx.obj.session = ctx.obj.service.session


from nextcodecli.commands.pipelines.status import status
from nextcodecli.commands.pipelines.list import list_pipelines
from nextcodecli.commands.pipelines.jobs import jobs
from nextcodecli.commands.pipelines.job import job
from nextcodecli.commands.pipelines.run import run

cli.add_command(status)
cli.add_command(list_pipelines)
cli.add_command(jobs)
cli.add_command(job)
cli.add_command(run)

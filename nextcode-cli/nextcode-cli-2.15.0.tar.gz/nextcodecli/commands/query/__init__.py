#!/usr/bin/env python

import click

from functools import wraps

from nextcode import get_service
from nextcode.exceptions import ServerError, InvalidProfile
from nextcodecli.utils import print_error, abort, check_profile

status_to_color = {
    'PENDING': 'yellow',
    'COMPLETED': 'green',
    'STARTED': 'yellow',
    'ERROR': 'red',
    'CANCELLED': 'white',
}


def check_project(func):
    @wraps(func)
    def _check(*args, **kwargs):
        ctx = click.get_current_context()
        svc = ctx.obj.service
        if not svc.project:
            abort("Please set a project by running: nextcode query project [name]")
        else:
            return func(*args, **kwargs)

    return _check


@click.group()
@click.pass_context
def cli(ctx):
    """Root subcommand for query api functionality.

    This command allows you to run GOR queries against the selected server.
    Before running a query you must select a project with 'nextcode query project [name]'.

    You must have access to the project in CSA in order to run queries. If needed you can
    user the 'nextcode csa' command to add yourself to a project, provided you have a CSA
    admin username and password to give yourself the roles."""
    if ctx.obj.service is None:
        check_profile(ctx)
        ctx.obj.service = ctx.obj.client.service("query")


from nextcodecli.commands.query.run import (
    run,
    project,
    info,
    download,
    results,
    cancel,
    list_queries,
    progress,
    details,
    wakeup,
)
from nextcodecli.commands.query.templates import templates
from nextcodecli.commands.query.status import status

cli.add_command(run)
cli.add_command(project)
cli.add_command(info)
cli.add_command(download)
cli.add_command(results)
cli.add_command(cancel)
cli.add_command(progress)
cli.add_command(list_queries)
cli.add_command(details)
cli.add_command(wakeup)

cli.add_command(templates)

cli.add_command(status)

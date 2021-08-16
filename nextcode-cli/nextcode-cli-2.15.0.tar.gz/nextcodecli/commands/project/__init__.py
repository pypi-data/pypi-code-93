#!/usr/bin/env python

import click

from functools import wraps

from nextcode import get_service
from nextcode.exceptions import ServerError, InvalidProfile
from nextcodecli.utils import print_error, abort, check_profile


def check_project(func):
    @wraps(func)
    def _check(*args, **kwargs):
        ctx = click.get_current_context()
        svc = ctx.obj.service
        if not svc.project:
            abort("Please set a project by running: nextcode setproject [name]")
        else:
            return func(*args, **kwargs)

    return _check


@click.group()
@click.pass_context
def cli(ctx):
    """Root subcommand for project api functionality."""
    if ctx.obj.service is None:
        check_profile(ctx)
        ctx.obj.service = ctx.obj.client.service("project")


from nextcodecli.commands.project.fileaccess import (
    list_bucket,
    upload,
    download,
    delete,
    head,
    credentials,
)
from nextcodecli.commands.project.status import status, create, update, view
from nextcodecli.commands.project.users import users

cli.add_command(list_bucket)
cli.add_command(upload)
cli.add_command(download)
cli.add_command(delete)
cli.add_command(head)
cli.add_command(status)
cli.add_command(users)
cli.add_command(create)
cli.add_command(update)
cli.add_command(view)
cli.add_command(credentials)

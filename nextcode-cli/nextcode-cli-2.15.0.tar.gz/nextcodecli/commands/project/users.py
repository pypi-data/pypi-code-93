#!/usr/bin/env python
import click
import sys
import collections
from tabulate import tabulate
import dateutil
import yaml
from pathlib import Path

from nextcode.exceptions import ServerError
from nextcode.services.project.exceptions import ProjectError

from ...utils import print_tab, dumps, get_logger, abort

log = get_logger(name='commands.project', level='INFO')


@click.group(help="Project user management")
def users():
    pass


@users.command()
@click.option(
    '--raw', 'is_raw', is_flag=True, default=False, help='Raw JSON response from endpoint'
)
@click.pass_context
def list(ctx, is_raw):
    """
    List all users in this project
    """
    svc = ctx.obj.service
    try:
        users = svc.get_users_in_project()
    except ServerError as ex:
        abort(ex)
    if is_raw:
        print(dumps(users))
        return
    data = []
    for u in users:
        data.append((u["user_id"], u["user"], ", ".join(u["policies"])))
    tbl = tabulate(data, headers=["user_id", "user_name", "policies"])
    print(tbl)


@users.command()
@click.argument('user_name', required=True)
@click.option(
    '--roles', '-r', 'policies_string', default=None, help='Comma-separated list of policies'
)
@click.pass_context
def add(ctx, user_name, policies_string):
    """
    Add a user to the current project
    """
    svc = ctx.obj.service
    policies = []
    if policies_string:
        policies = [p.strip() for p in policies_string.split(",")]
    try:
        if policies:
            ret = svc.add_user_to_project(user_name=user_name, policies=policies)
        else:
            ret = svc.add_user_to_project(user_name=user_name)
    except ProjectError as ex:
        abort(ex)
    click.secho(
        f"User {user_name} has been added to project {ret['project']} with roles {', '.join(ret['policies'])}",
        bold=True,
    )


@users.command()
@click.argument('user_name', required=True)
@click.pass_context
def remove(ctx, user_name):
    """
    Remove a user from the current project
    """
    svc = ctx.obj.service
    try:
        svc.remove_user_from_project(user_name=user_name)
    except ProjectError as ex:
        abort(ex)
    click.secho(f"User {user_name} has been removed from project {svc.project_name}", bold=True)

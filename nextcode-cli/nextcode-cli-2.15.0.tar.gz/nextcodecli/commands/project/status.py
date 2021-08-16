#!/usr/bin/env python

import click
from nextcode.config import get_default_profile
import nextcodecli
from nextcodecli.utils import dumps, print_table
from ...utils import abort, fmt_date


@click.command(help="Show the status of the project api")
@click.option('-r', '--raw', 'is_raw', is_flag=True, help='Dump raw json response')
@click.pass_context
def status(ctx, is_raw):
    svc = ctx.obj.service
    profile_name = get_default_profile()
    if is_raw:
        dct = svc.session.root_info
        dct.update({'version': nextcodecli.get_version_string(), 'profile': profile_name})
        click.echo(dumps(dct))
    else:
        click.echo(nextcodecli.get_version_string() + '\n')

        click.echo("{0:20}{1}".format('profile', profile_name))
        click.echo('')
        click.echo("Contacting project api '%s'... " % svc.base_url, nl=False)

        click.echo("Success!\n\nAPI deployment information:")
        print_table(svc.build_info)

        svc = ctx.obj.service
        click.echo("{0:20}{1}".format("Current project", svc.project_name))
        click.echo("{0:20}{1}".format("Admin", "Yes" if svc.current_user["admin"] else "No"))
        click.echo("{0:20}{1}".format("Minio Url", svc.session.root_info["app_info"]["minio_url"]))
        click.echo('')


@click.command(help="Create the current project in the project api")
@click.pass_context
def create(ctx):
    svc = ctx.obj.service
    try:
        project = svc.create_project()
    except Exception as e:
        abort(e)
    click.echo(dumps(project))


@click.command(help="Update the current project in the project api")
@click.option('-t', '--title', help='Project title')
@click.option('-d', '--description', help='Project description')
@click.pass_context
def update(ctx, title, description):
    svc = ctx.obj.service
    project = svc.project
    data = {}
    if title:
        data["title"] = title
    if description:
        data["description"] = description
    try:
        project = svc.session.put(project["links"]["self"], json=data)
    except Exception as e:
        abort(e)
    click.echo(dumps(project.json()))


@click.command(help="View project information")
@click.option('-r', '--raw', 'is_raw', is_flag=True, help='Dump raw json response')
@click.pass_context
def view(ctx, is_raw):
    svc = ctx.obj.service
    project = svc.project
    if is_raw:
        click.echo(dumps(project))
        return
    if not project:
        abort(f"Project {svc.project_name} not found. Please run 'nextcode project create'")
    click.echo("{0:20}{1}".format("Project name", click.style(project["project_name"], bold=True)))
    click.echo("{0:20}{1}".format("Project ID", project["project_id"]))
    click.echo("{0:20}{1}".format("Title", project["title"]))
    click.echo("{0:20}{1}".format("Description", project["description"]))
    click.echo("{0:20}{1}".format("Create date", fmt_date(project["create_date"])))

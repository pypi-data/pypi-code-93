#!/usr/bin/env python

import click
from click import echo, secho, pass_context, command, argument, option
import dateutil
from tabulate import tabulate

from nextcodecli.utils import dumps


@command(help="List projects")
@option('--raw', 'is_raw', is_flag=True, help='Dump raw json for further processing')
@pass_context
def projects(ctx, is_raw):
    projects = ctx.obj.service.get_projects()
    if is_raw:
        click.echo(dumps(projects))
        return

    fields = ['project_id', 'internal_name', 'create_date', 'csa_file_path']
    table = []
    for project in projects:
        lst = []
        for f in fields:
            v = project[f] or 'N/A'
            if f in ('create_date',):
                try:
                    v = dateutil.parser.parse(v).strftime("%Y-%m-%d %H:%M")
                except Exception:
                    v = ''
            lst.append(v)

        table.append(lst)
    tbl = tabulate(table, headers=fields)
    click.echo(tbl)

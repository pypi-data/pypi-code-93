#!/usr/bin/env python

import click
from nextcodecli.utils import dumps, print_tab


@click.command(name='list', help="List available pipelines")
@click.option('-r', '--raw', 'is_raw', is_flag=True, help='Dump raw json response')
@click.pass_context
def list_pipelines(ctx, is_raw):
    session = ctx.obj.session
    resp = session.get(session.url_from_endpoint('pipelines'))
    resp.raise_for_status()
    pipelines = []
    for pipeline in resp.json()['pipelines']:
        resp = session.get(pipeline['links']['self'])
        pipelines.append(resp.json())
    if is_raw:
        click.echo(dumps(pipelines))
    else:
        for pipeline in pipelines:
            print_tab('name', pipeline['name'])
            print_tab('description', pipeline['description'])
            print_tab('author', pipeline['author'])
            print_tab('version', pipeline['version'])
            click.echo('')

#!/usr/bin/env python

import click
from nextcodecli import get_version_string
from nextcodecli.utils import dumps, print_table


@click.command(help="Show the status of the pipelines-service")
@click.option('-r', '--raw', 'is_raw', is_flag=True, help='Dump raw json response')
@click.pass_context
def status(ctx, is_raw):
    svc = ctx.obj.service
    session = svc.session
    profile_config = svc.client.profile.content
    profile_name = svc.client.profile_name
    if is_raw:
        dct = {
            'version': get_version_string(),
            'profile': profile_name,
            'profile_config': profile_config,
        }
        for key in ('build_info', 'app_info', 'endpoints', 'current_user'):
            dct[key] = getattr(svc, key, None)
        resp = session.get(session.url_from_endpoint('pipelines'))
        dct['pipelines'] = [p['name'] for p in resp.json()['pipelines']]
        click.echo(dumps(dct))
    else:
        click.echo(get_version_string() + '\n')

        click.echo("{0:20}{1}".format('profile', profile_name))
        click.echo('')
        print_table(svc.build_info)
        print_table(svc.app_info)

        click.echo('')

#!/usr/bin/env python

import click
from nextcode.config import get_default_profile
import nextcodecli
from nextcodecli.utils import dumps, print_table


@click.command(help="Show the status of the gor query api")
@click.option('-r', '--raw', 'is_raw', is_flag=True, help='Dump raw json response')
@click.pass_context
def status(ctx, is_raw):
    svc = ctx.obj.service
    profile_name = get_default_profile()
    if is_raw:
        dct = {'version': nextcodecli.get_version_string(), 'profile': profile_name}
        for key in ('build_info', 'app_info', 'endpoints', 'current_user'):
            dct[key] = getattr(svc.session, key, None)
        click.echo(dumps(dct))
    else:
        click.echo(nextcodecli.get_version_string() + '\n')

        click.echo("{0:20}{1}".format('profile', profile_name))
        click.echo('')
        click.echo("Contacting gor query api '%s'... " % svc.base_url, nl=False)

        click.echo("Success!\n\nAPI deployment information:")
        print_table(svc.build_info)

        svc = ctx.obj.service
        click.echo("{0:20}{1}".format("Current project", svc.project))
        click.echo('')

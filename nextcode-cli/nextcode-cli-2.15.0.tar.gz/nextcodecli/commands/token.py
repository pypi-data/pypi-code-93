#!/usr/bin/env python

import click
from datetime import datetime
from nextcode import Client
from nextcode.config import get_default_profile, clear_cache
from nextcodecli.utils import print_tab, dumps
from nextcode.utils import decode_token


@click.command()
@click.option(
    '-r',
    '--raw',
    'is_raw',
    is_flag=True,
    help='Return decoded token as json as well as the token itself',
)
def cli(is_raw):
    """
    Print out an access token for the current profile
    """
    clear_cache()
    client = Client()
    token = client.get_access_token(decode=False)

    payload = decode_token(token)
    profile = get_default_profile()
    if is_raw:
        ret = {"token": token, "payload": payload, "profile": profile}
        click.echo(dumps(ret))
        return

    click.echo(
        "Access token for services in the '%s' profile. Use by adding 'Authorization: Bearer xxx' request header"
        % profile
    )
    print_tab("Issuer", payload['iss'])
    exp = datetime.utcfromtimestamp(payload['exp'])
    diff = exp - datetime.utcnow()
    print_tab("Expires in", diff)
    click.echo('\n' + token + '\n')

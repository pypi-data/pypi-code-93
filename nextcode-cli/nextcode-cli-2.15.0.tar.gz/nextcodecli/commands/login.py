#!/usr/bin/env python

import os
import sys

import click
from click import pass_context, command, option, secho, echo
import requests
import logging

from nextcode.config import get_profile_config, get_default_profile, create_profile
from nextcode.exceptions import InvalidProfile, InvalidToken
from nextcode.client import get_api_key
from nextcodecli.utils import abort, dumps

log = logging.getLogger(__name__)


@command()
@option('-u', '--username')
@option('-p', '--password')
@option('-r', '--realm', default='wuxinextcode.com')
@option(
    '-h',
    '--host',
    default=None,
    help="Host override if not using profile, e.g. platform.wuxinextcodedev.com",
)
@option(
    '-t',
    '--token',
    'is_token',
    is_flag=True,
    help="Return refresh token instead of writing into current profile",
)
@pass_context
def cli(ctx, username, password, realm, host, is_token):
    """
    Authenticate against keycloak.
    """
    try:
        config = get_profile_config()
    except InvalidProfile as ex:
        secho(str(ex), fg="red")
        abort("Please create a profile with: nextcode profile add [name]")
    profile_name = get_default_profile()

    if username and password:
        if not is_token:
            echo("Authenticating from commandline parameters")
        host = host or config["root_url"]
        try:
            api_key = get_api_key(host, username, password, realm=realm)
        except InvalidToken as ex:
            abort(ex)
        if is_token:
            click.echo(api_key)
            return
        create_profile(profile_name, api_key=api_key, root_url=host)
        click.secho("Profile {} has been updated with api key".format(profile_name), bold=True)

    else:
        if host:
            root_url = "https://%s" % host
        else:
            root_url = config["root_url"]
        login_server = root_url + "/api-key-service"

        if login_server:
            echo("Launching login webpage ==> Please authenticate and then press continue.")
            click.launch(login_server)
            click.pause()
        else:
            click.secho(
                "No login server configured. Please aquire a refresh_token from "
                "somewhere manually.",
                fg='yellow',
            )

        # Note: readline must be imported for click.prompt() to accept long strings. Don't ask me why.
        import readline

        api_key = click.prompt("API Key", type=str)
        try:
            create_profile(profile_name, api_key=api_key)
        except InvalidProfile as ex:
            abort(ex)

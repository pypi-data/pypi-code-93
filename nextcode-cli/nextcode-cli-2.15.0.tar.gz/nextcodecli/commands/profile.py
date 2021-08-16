#!/usr/bin/env python

import os
import requests
from urllib.parse import urlsplit, urljoin

import click
from click.utils import echo

from nextcode.config import (
    root_config_folder,
    get_profiles,
    get_default_profile,
    set_default_profile,
    create_profile,
    delete_profile,
)
from nextcode.exceptions import InvalidProfile
from nextcodecli.utils import abort


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """
    Configure server profile to use.

    Note that you can override the currently selected profile with: export NEXTCODE_PROFILE=[profile name]
    """
    if ctx.invoked_subcommand is None:
        ctx.invoke(view, profile=get_default_profile())
        echo(ctx.get_help())


@cli.command()
@click.pass_context
def list(ctx):
    """lists all available profiles."""
    click.echo('Available profiles:')
    for profile_name in sorted(get_profiles()):
        if get_default_profile() == profile_name:
            click.secho('==> %s <==' % profile_name, fg='green')
        else:
            click.echo('    %s' % profile_name)
    click.echo('')


@cli.command()
@click.argument('profile')
@click.pass_context
def view(ctx, profile):
    """displays content for a given profile name."""
    if not get_profiles():
        abort("No profiles are currently set up. Please run 'nextcode profile add [name]' to start")

    profile = (profile or "").lower()
    click.secho('Current profile: %s' % get_default_profile(), fg='green')
    profile_config = get_profiles().get(profile)
    if not profile_config:
        click.secho('Profile %s not found' % profile, fg='red')
        ctx.invoke(list)
        return

    click.echo('Viewing profile configuration for %s' % profile)
    for k, v in sorted(profile_config.items()):
        click.echo("   {0:20}{1}".format(k, v))
    click.echo('')


@cli.command()
@click.argument('profile')
@click.pass_context
def set(ctx, profile):
    """sets the profile given by name as 'current'."""
    profile = profile.lower()
    try:
        set_default_profile(profile)
    except Exception as e:
        click.secho(str(e), fg='red')
        click.echo("View available profiles with 'nextcode profile list'")
        return
    else:
        click.secho('Your profile has been changed to %s' % profile, bold=True)

    ctx.invoke(view, profile=profile)


@cli.command()
@click.pass_context
def edit(ctx):
    """open up the config.yaml file"""
    full_filename = os.path.join(root_config_folder, "config.yaml")
    click.echo("Editing config file located at %s" % (full_filename))

    click.echo("Modify your config and close the file")
    click.edit(filename=full_filename, require_save=True)


@cli.command()
@click.argument('profile')
@click.option(
    '-d', '--domain', prompt="Domain name of the service (f.ex. platform.wuxinextcodedev.com)"
)
@click.option('-k', '--api-key', help="API Key (if not set a browser will open)")
@click.option('-r', '--replace', is_flag=True, default=False, help="Replace an existing profile")
@click.option(
    '-s',
    '--skip-auth',
    is_flag=True,
    default=False,
    help="Skip authenetication (for local development)",
)
@click.pass_context
def add(ctx, profile, domain, api_key, replace, skip_auth):
    """Creates a new profile of the specified name and allows you to configure it"""
    profile = profile.lower()
    if profile in get_profiles() and not replace:
        click.secho(
            "Profile '{}' already exists. Use --replace if you want to override it.".format(
                profile
            ),
            fg='red',
        )
        return

    if not domain.startswith("http"):
        domain = "https://{}".format(domain)
    # check for common mistakes in domain name
    if not domain or ':' in domain or '/' in domain:
        parts = urlsplit(domain)
        domain = "{}://{}".format(parts.scheme, parts.netloc)

    if not skip_auth:
        if not api_key:
            reachable = True
            try:
                url = '%s/api-key-service' % domain
                resp = requests.get(url, timeout=2)
                resp.raise_for_status()
            except Exception:
                click.secho("%s is not reachable." % url, fg='red')
                reachable = False
                if not click.confirm("Are you sure you want to add this domain?"):
                    return

            if reachable:
                click.echo(
                    "Launching login webpage {} ==> Please retrieve API Key from browser".format(
                        url
                    )
                )
                click.launch(url)
                click.pause()
            else:
                click.secho("Please aquire an api_key from " "somewhere manually.", fg='yellow')
            # Note: readline must be imported for click.prompt() to accept long strings. Don't ask me why.
            import readline

            api_key = click.prompt("API Key", type=str)

    try:
        create_profile(profile, api_key=api_key, root_url=domain, skip_auth=skip_auth)
    except InvalidProfile as ex:
        abort(ex)
    set_default_profile(profile)
    click.echo(
        "Profile has been added and is now active. "
        "If you want to change it please run: nextcode profile edit"
    )


@cli.command()
@click.argument('profile')
@click.pass_context
def delete(ctx, profile):
    """accepts a profile name and deletes it."""
    profile = profile.lower()
    delete_profile(profile)
    click.secho("Profile '%s' has been deleted" % profile, bold=True)


def custom_error(main_command):
    def show(self, file=None):
        click.secho('Current profile: %s' % get_default_profile(), fg='green')
        click.echo(main_command.get_help(self.ctx))

    click.exceptions.UsageError.show = show


custom_error(cli)

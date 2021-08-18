import os
import sys
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(project_root)

import sentry_sdk
sentry_sdk.init(
    "https://509ae343ea5542c0a39ebc92a1b6ee2f@o386227.ingest.sentry.io/5779468",
    traces_sample_rate=1.0
)

import time

import requests
import typer

from savvihub.api.exceptions import NotFoundAPIException, InvalidTokenAPIException
from savvihub.api.savvihub import SavviHubClient
from savvihub.cli.commands.cluster import cluster_app
from savvihub.cli.commands.dataset import dataset_app
from savvihub.cli.commands.experiment import experiment_app
from savvihub.cli.commands.project import project_app
from savvihub.cli.commands.ssh_keys import ssh_keys_app
from savvihub.cli.commands.sweep import sweep_app
from savvihub.cli.commands.volume import volume_app
from savvihub.cli.commands.workspace import workspace_app
from savvihub.cli.config_loader import GlobalConfigLoader
from savvihub.cli.constants import WEB_HOST
from savvihub.cli.exceptions import ExitException
from savvihub.cli.typer import Typer, Context
from savvihub.cli.utils import get_default_organization
from savvihub.common.constants import API_HOST, DEBUG, __VERSION__


app = Typer()
app.add_typer(cluster_app, name='cluster')
app.add_typer(dataset_app, name='dataset')
app.add_typer(experiment_app, name='experiment')
app.add_typer(project_app, name='project')
app.add_typer(ssh_keys_app, name='ssh-keys')
app.add_typer(sweep_app, name='sweep', hidden=True)
app.add_typer(volume_app, name='volume', hidden=True)
app.add_typer(workspace_app, name='workspace')


def version_callback(value: bool):
    if value:
        typer.echo(f'SavviHub CLI Version: {__VERSION__}')
        sys.exit(0)


@app.callback()
def main(
    version: bool = typer.Option(None, '--version', callback=version_callback,
                                 help='Print the current SavviHub CLI version.'),
):
    """
    SavviHub Command Line Interface (CLI)
    """
    if DEBUG:
        typer.echo(f'SavviHub CLI Version: {__VERSION__}')


@app.command(hidden=True)
def ping():
    """
    Ping to the SavviHub server
    """
    res = requests.get(API_HOST + '/api/v1/ping')
    typer.echo(f'Response code: {res.status_code}, Response text: {res.text}')


@app.command()
def login(
    token: str = typer.Option(None, '-t', '--token'),
):
    """
    Initialize SavviHub Command Line Interface (CLI)
    """

    def update_token():
        client = SavviHubClient()
        cli_token = client.signin_cli_token().cli_token
        typer.echo(f'Please grant CLI access from the URL below.\n'
                   f'{WEB_HOST}/cli/grant-access?token={cli_token}')
        typer.echo('Waiting...\n')

        start_time = time.time()
        while True:
            if time.time() - start_time >= 160:
                raise ExitException('Login timeout. Please try again.')

            check_signin_response = client.check_signin(cli_token)
            if not check_signin_response.signin_success:
                time.sleep(3)
                continue

            return check_signin_response.access_token

    if token is None:
        token = update_token()

    client = SavviHubClient(auth_header={'Authorization': f'Token {token}'})
    me = client.get_my_info()
    if me:
        typer.echo(f'Hello, {me.username}!\n')
    else:
        typer.echo('Token expired or invalid token.')
        token = update_token()

    config = GlobalConfigLoader()
    config.token = token
    config.organization = get_default_organization(client).name
    typer.echo(f'Successfully configured in {config.filename}')


@app.command()
def status(
    ctx: Context,
):
    """
    Show current user and default organization
    """
    if ctx.global_config.token is None:
        raise ExitException('Not logged in. Please run `savvihub login`.')

    try:
        user = ctx.authenticated_client.get_my_info()
    except (NotFoundAPIException, InvalidTokenAPIException):
        raise ExitException('Token expired. Please run `savvihub login`.')

    typer.echo(f'Username: {user.username}\n'
               f'Email: {user.email}')

    if ctx.global_config.organization is None:
        typer.echo('Default organization is not set. Please run `savvihub set-default-organization`.')
    else:
        typer.echo(f'Default organization: {ctx.global_config.organization}')


@app.command(user_required=True)
def set_default_organization(
    ctx: Context,
):
    """
    Set default organization
    """
    organization = get_default_organization(ctx.authenticated_client)
    ctx.global_config.organization = organization.name


if __name__ == '__main__':
    app()

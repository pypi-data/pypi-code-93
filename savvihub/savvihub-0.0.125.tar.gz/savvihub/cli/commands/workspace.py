import os
import urllib.parse
from pathlib import Path
from zipfile import ZipFile

import inquirer
import paramiko
import typer

from savvihub.api.exceptions import NotFoundAPIException
from savvihub.api.zipper import Zipper
from savvihub.cli.commands.volume import volume_file_copy
from savvihub.cli.exceptions import ExitException
from savvihub.cli.inputs.organization import organization_name_option
from savvihub.cli.inputs.ssh import ssh_private_key_path_callback
from savvihub.cli.typer import Typer, Context
from savvihub.common.utils import parse_time_to_ago

workspace_app = Typer()


@workspace_app.callback()
def main():
    """
    Manage workspaces
    """


@workspace_app.command(user_required=True)
def ssh(
    ctx: Context,
    organization_name: str = organization_name_option,
    ssh_private_key_path: str = typer.Option(None, '--key-path', callback=ssh_private_key_path_callback, help='SSH private key path.'),
):
    """
    Connect to a running workspace via SSH.
    """
    workspace_list_response = ctx.authenticated_client.workspace_list(organization_name, 'running')
    running_workspaces = workspace_list_response.results
    if len(running_workspaces) == 0:
        raise ExitException('There is no running workspace.')

    if len(running_workspaces) == 1:
        workspace = running_workspaces[0]
    else:
        workspace = inquirer.prompt([inquirer.List(
            'question',
            message='Select workspace',
            choices=[(f'{w.name} (created {parse_time_to_ago(w.created_dt)})', w) for w in running_workspaces],
        )], raise_keyboard_interrupt=True).get('question')

    ssh_endpoint = urllib.parse.urlparse(workspace.endpoints.ssh.endpoint)
    ssh_private_key_option = f' -i {ssh_private_key_path}' if ssh_private_key_path else ''
    os.system(f'ssh -p {ssh_endpoint.port}{ssh_private_key_option} vessl@{ssh_endpoint.hostname}')


@workspace_app.command(user_required=True)
def vscode(
    ctx: Context,
    organization_name: str = organization_name_option,
    ssh_private_key_path: str = typer.Option(None, '--key-path', callback=ssh_private_key_path_callback,
                                             help='SSH private key path.'),
):
    """
    Update .ssh/config file for VSCode Remote-SSH plugin
    """
    workspace_list_response = ctx.authenticated_client.workspace_list(organization_name, 'running')
    running_workspaces = workspace_list_response.results
    if len(running_workspaces) == 0:
        raise ExitException('There is no running workspace.')

    ssh_config = paramiko.SSHConfig()
    ssh_config.parse(open(f'{Path.home()}/.ssh/config'))
    hostname_set = ssh_config.get_hostnames()

    for workspace in running_workspaces:
        hostname = f'{workspace.name}-{int(workspace.created_dt.timestamp())}'
        if hostname in hostname_set:
            continue

        ssh_endpoint = urllib.parse.urlparse(workspace.endpoints.ssh.endpoint)
        config_value = f'''
Host {hostname}
    User vessl
    Hostname {ssh_endpoint.hostname}
    Port {ssh_endpoint.port}
    StrictHostKeyChecking accept-new
    CheckHostIP no
'''
        if ssh_private_key_path:
            config_value += f'    IdentityFile {ssh_private_key_path}\n'

        with open(f'{Path.home()}/.ssh/config', 'a') as f:
            f.write(config_value)

    typer.echo(f'Successfully updated {Path.home()}/.ssh/config')


@workspace_app.command(user_required=True)
def backup(ctx: Context):
    """
    Backup the home directory of the workspace
    (Should be called inside a workspace)
    """

    workspace_id = ctx.global_config.workspace
    if not workspace_id:
        raise ExitException('This command should be called inside a workspace.')

    organization_name = ctx.global_config.organization
    try:
        workspace = ctx.authenticated_client.workspace_read(organization_name, workspace_id)
    except NotFoundAPIException:
        raise ExitException(f'Workspace not found.\n'
                            f'Did you change the default organization?')

    zipper = Zipper('/tmp/workspace-backup.zip', 'w')
    zipper.zipdir(str(Path.home()), zipper)
    zipper.close()

    volume_file_copy(
        ctx,
        source_volume_id=None,
        source_path=zipper.filename,
        dest_volume_id=workspace.backup_volume_id,
        dest_path=os.path.basename(zipper.filename),
        recursive=False,
        watch=False,
    )

    ctx.authenticated_client.workspace_update_backup_dt(workspace_id)


@workspace_app.command(user_required=True)
def restore(
    ctx: Context,
    organization_name: str = organization_name_option,
):
    """
    Restore the home directory from the previous backup
    (Should be called inside a workspace)
    """
    workspace_id = ctx.global_config.workspace
    if not workspace_id:
        raise ExitException('This command should be called inside a workspace.')

    workspace_list_response = ctx.authenticated_client.workspace_list(organization_name, None)
    backup_workspaces = [w for w in workspace_list_response.results if w.last_backup_dt is not None]
    if len(backup_workspaces) == 0:
        raise ExitException('Available workspace backup not found.')

    workspace = inquirer.prompt([inquirer.List(
        'question',
        message='Select workspace',
        choices=[(f'{w.name} (backup created {parse_time_to_ago(w.last_backup_dt)})', w) for w in backup_workspaces],
    )], raise_keyboard_interrupt=True).get('question')

    volume_file_copy(
        ctx,
        source_volume_id=workspace.backup_volume_id,
        source_path='workspace-backup.zip',
        dest_volume_id=None,
        dest_path='/tmp/workspace-backup.zip',
        recursive=False,
        watch=False,
    )

    z = ZipFile('/tmp/workspace-backup.zip')
    z.extractall(str(Path.home()))

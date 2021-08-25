import subprocess
from typing import Dict, Optional

import click

from grid.cli import rich_click
from grid.cli.cli.grid_run import _check_run_name_is_valid, _get_instance_types, _resolve_instance_type_nickname
from grid.cli.cli.utilities import read_config_callback, validate_config, validate_disk_size_callback
from grid.cli.client import Grid
import grid.cli.globals as env
from grid.cli.types import ObservableType
from grid.cli.utilities import check_description_isnt_too_long
from grid.sdk.action import validate_and_configure_datastore
from grid.sdk.utils.name_generator import unique_name

WARNING_STR = click.style('WARNING', fg='yellow')


def _generate_default_interactive_config(
    instance_type: str,
    cluster: Optional[str] = None,
    datastore_name: Optional[str] = None,
    datastore_version: Optional[str] = None,
    datastore_mount_dir: Optional[str] = None,
    disk_size: Optional[int] = None,
    use_spot: Optional[bool] = None
):
    """
    Generates a new default config file for user if user hasn't
    submitted one.
    """
    # These configs need to be cleaned-up. We don't really need
    # anything in provider apart from cluster
    provider = {'vendor': "aws", 'credentials': "n/a", 'region': 'us-east-1'}
    if cluster:
        provider['cluster'] = cluster

    _grid_config = {
        'compute': {
            'provider': provider,
            'train': {
                'instance': instance_type,
                'disk_size': disk_size,
                'gpus': 0,  # Required, but ignored.
                'datastore_name': datastore_name,
                'datastore_version': datastore_version,
                'datastore_mount_dir': datastore_mount_dir,
                'use_spot': use_spot or False,
            }
        }
    }

    #  Print debug message if in debug mode.
    if env.DEBUG:
        click.echo('Grid Config used:')
        click.echo(_grid_config)

    return _grid_config


@rich_click.group(invoke_without_command=True)
@click.pass_context
@click.option(
    '--global',
    'is_global',
    type=bool,
    is_flag=True,
    help='Fetch sessions from everyone in the team when flag is passed'
)
def session(ctx, is_global: bool) -> None:
    """Manage Sessions workflows."""
    client = Grid()
    if ctx.invoked_subcommand is None:
        # Get the status of the interactive observables.
        kind = ObservableType.INTERACTIVE
        client.status(kind=kind, follow=False, is_global=is_global)
    elif is_global:
        click.echo(f"{WARNING_STR}: --global flag doesn't have any effect when invoked with a subcommand")


@session.command(cls=rich_click.deprecate_grid_options())
@click.option(
    '--config',
    'config',
    type=click.File('r'),
    required=False,
    callback=read_config_callback,
    help='Path to Grid config YML'
)
@click.option('--name', 'name', type=str, required=False, help='Name for this run', callback=_check_run_name_is_valid)
@click.option(
    '--description',
    'description',
    type=str,
    required=False,
    help='Session description; useful for note-keeping.',
    callback=check_description_isnt_too_long
)
@click.option('--cluster', 'cluster', type=str, required=False, help='Cluster to run on')
@click.option(
    '--instance_type',
    'instance_type',
    type=str,
    default='t2.medium',
    callback=_resolve_instance_type_nickname,
    help='Instance type to start session in.',
    autocompletion=_get_instance_types
)
@click.option(
    '--use_spot',
    'use_spot',
    is_flag=True,
    required=False,
    help='Use spot instance. The spot instances, or preemptive instance can be shut down at will'
)
@click.option(
    '--disk_size',
    'disk_size',
    type=int,
    required=False,
    default=200,
    callback=validate_disk_size_callback,
    help='The disk size in GB to allocate to the session.'
)
@click.option(
    '--datastore_name', 'datastore_name', type=str, required=False, help='Datastore name to be mounted in the session.'
)
@click.option(
    '--datastore_version',
    'datastore_version',
    type=str,
    required=False,
    help='Datastore version to be mounted in the session.'
)
@click.option(
    '--datastore_mount_dir',
    'datastore_mount_dir',
    type=str,
    required=False,
    help='Absolute path to mount Datastore in the session (defaults to ~/[datastore_name]).'
)
def create(
    config: Optional[Dict], name: Optional[str], description: Optional[str], cluster: Optional[str], instance_type: str,
    datastore_name: Optional[str], datastore_version: Optional[str], datastore_mount_dir: Optional[str],
    disk_size: Optional[int], use_spot: Optional[bool]
) -> None:
    """Creates a session."""
    client = Grid()
    client.check_is_blocked()

    # make a fun random name when user does not pass in a name
    if name is None:
        name = unique_name()

    #  If the user has not passed a grid config file,
    #  then generate one with a set of default options.
    #  We'll add a default instance and the user's
    #  default credentials.
    if not config:
        _grid_config = _generate_default_interactive_config(
            datastore_name=datastore_name,
            datastore_version=datastore_version,
            datastore_mount_dir=datastore_mount_dir,
            cluster=cluster,
            instance_type=instance_type,
            disk_size=disk_size,
            use_spot=use_spot
        )

    else:
        _grid_config = config

    validate_config(cfg=_grid_config)
    validate_and_configure_datastore(grid_config=_grid_config)

    #  Send to client.
    client.create_interactive_node(config=_grid_config, name=name, description=description)


@session.command()
@rich_click.argument('interactive_node', type=str, nargs=1)
def pause(interactive_node: str) -> None:
    """Pauses a session."""
    client = Grid()
    client.pause_interactive_node(interactive_node_name=interactive_node)


@session.command()
@rich_click.argument('interactive_node', type=str, nargs=1)
def resume(interactive_node: str) -> None:
    """Resumes a session."""
    client = Grid()
    client.resume_interactive_node(interactive_node_name=interactive_node)


@session.command()
@rich_click.argument('interactive_node', type=str, nargs=1)
def delete(interactive_node: str) -> None:
    """Deletes a session."""
    client = Grid()
    client.delete_interactive_node(interactive_node_name=interactive_node)


def _update_ssh_config_and_check_ixsession_status(ctx, param, value: str) -> int:
    """
    This updates the SSH config for interactive nodes and
    also checks if those nodes can be interacted with SSH
    before attempting an operation. This prevents SSHing into
    nodes that are not un a running state, e.g. paused or pending.

    This manages a section within user's ssh config file
    for all interactive nodes shh config details

    Afterwards you can use systems ssh & related utilities
    (sshfs, rsync, ansible, whatever) with interactive nodes
    directly

    The default file is ~/.ssh/config and  can be changed via
    envvar GRID_SSH_CONFIG

    Returns
    --------
    value: str
        Unmodified value if valid
    """
    client = Grid()
    nodes = client.sync_ssh_config()

    click.echo(f"Sync config for {len(nodes)} interactive nodes")

    target_ixsession = None
    for node in nodes:
        if node["name"] == value:
            target_ixsession = node

    # Check if interactive session exists at all
    if not target_ixsession:
        session_names = [n["name"] for n in nodes]
        raise click.BadArgumentUsage(
            f"Interactive session {value} does not exist. "
            f"Available Interactive Sessions are: {', '.join(session_names)}"
        )

    # Check if the node is in 'running' status
    if target_ixsession["status"] != "running":
        running_ixsessions = [n["name"] for n in nodes if n["status"] == "running"]
        raise click.BadArgumentUsage(
            f"Interactive session {value} is not ready. "
            f"Sessions that are ready to SSH are: {', '.join(running_ixsessions)}"
        )

    return value


@session.command()
@rich_click.argument(
    'node_name',
    type=str,
    callback=_update_ssh_config_and_check_ixsession_status,
    help="The name of the node. This command executes ssh <node name>.",
)
@rich_click.argument('ssh_args', nargs=-1, type=click.UNPROCESSED, help="Arguments to be forwarded to the SSH command.")
def ssh(node_name, ssh_args):
    """
    SSH in to interactive nodes.

    If you'd like the full power of ssh, you can use any ssh client and
    do `ssh <node_name>`. This command is stripped down version of it.

    Example:

        1. Path to custom key:

        grid session ssh satisfied-rabbit-962 -- -i ~/.ssh/my-key

        2. Custom ssh option:

        grid session ssh satisfied-rabbit-962 -- -o "StrictHostKeyChecking accept-new"
    """
    subprocess.check_call(['ssh', node_name, *ssh_args])


@session.command()
@rich_click.argument('interactive_node', type=str, nargs=1, callback=_update_ssh_config_and_check_ixsession_status)
@rich_click.argument('mount_dir', type=str, nargs=1)
def mount(interactive_node, mount_dir):
    r"""
    Mount session directory to local.

    To mount a filesystem use:
    ixNode:[dir] mountpoint

    Examples:
        # Mounts the home directory on the interactive node in dir data
        grid interactive mount bluberry-122 ./data

        # mounts ~/data directory on the interactive node to ./data
        grid interactive mount bluberry-122:~/data ./data

    To unmount it:
      fusermount3 -u mountpoint   # Linux
      umount mountpoint           # OS X, FreeBSD

    Under the hood this is just passing data to sshfs after syncing grid's interactive,
    i.e. this command is dumbed down sshfs

    See Also:
        grid sync-ssh-config --help
    """
    if ':' not in interactive_node:
        interactive_node += ":/home/jovyan"

    client = Grid()
    client.sync_ssh_config()

    try:
        subprocess.check_call(['sshfs', interactive_node, mount_dir])
    except FileNotFoundError:
        raise click.ClickException('Unable to mount: sshfs was not found')
    except subprocess.CalledProcessError as e:
        raise click.ClickException(f'Unable to mount: sshfs failed with code {e.returncode}')

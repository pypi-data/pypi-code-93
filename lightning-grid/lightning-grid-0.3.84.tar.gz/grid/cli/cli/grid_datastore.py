from typing import Optional

import click

from grid.cli import rich_click
from grid.cli.client import Grid
from grid.sdk._gql.queries import get_user
from grid.sdk.datastore import parse_name_from_source

WARNING_STR = click.style('WARNING', fg='yellow')


@click.group(invoke_without_command=True)
@click.pass_context
@click.option(
    '--global',
    'is_global',
    type=bool,
    is_flag=True,
    help='Fetch sessions from everyone in the team when flag is passed'
)
def datastore(ctx, is_global: bool) -> None:
    """Manages Datastore workflows."""
    client = Grid()

    if ctx.invoked_subcommand is None:
        client.list_datastores(is_global=is_global)
    elif is_global:
        click.echo(f"{WARNING_STR}: --global flag doesn't have any effect when invoked with a subcommand")


@datastore.command()
@rich_click.argument('session_name', nargs=1, help="The name of the session.")
@click.pass_context
def resume(ctx, session_name: str):
    """Resumes uploading a datastore."""
    client = Grid()
    if session_name == "list":
        client.list_resumable_datastore_sessions()
        return

    client.resume_datastore_session(session_name)


@datastore.command(cls=rich_click.deprecate_grid_options())
@click.option(
    '--source',
    required=True,
    help="""Source to create datastore from. This could either be a local directory (e.g: /opt/local_folder) or a remote
    HTTP URL pointing to a TAR file (e.g: http://some_domain/data.tar.gz)."""
)
@click.option('--name', type=str, required=False, help='Name of the datastore')
@click.option(
    '--compression',
    type=bool,
    required=False,
    help='Compresses datastores with GZIP when flag is passed.',
    default=False,
    is_flag=True
)
@click.option(
    '--cluster',
    type=str,
    required=False,
    help='cluster id to create the datastore on. (Bring Your Own Cloud Customers Only).'
)
@click.pass_context
def create(ctx, source: str, name: str, compression: bool = False, cluster: Optional[str] = None) -> None:
    """Creates a datastore."""
    client = Grid()
    user_data = get_user()
    client.check_is_blocked(user_data=user_data)

    if not name:
        name = parse_name_from_source(source)
    client.upload_datastore(source=source, name=name, compression=compression, cluster=cluster)


@datastore.command()
@click.pass_context
def list(ctx) -> None:
    """Lists datastores."""
    client = Grid()
    client.list_datastores()


@datastore.command(cls=rich_click.deprecate_grid_options())
@click.option('--name', type=str, required=True, help='Name of the datastore')
@click.option('--version', type=int, required=True, help='Version of the datastore')
@click.option(
    '--cluster',
    type=str,
    required=False,
    help='cluster id to delete the datastore from. (Bring Your Own Cloud Customers Only).'
)
@click.pass_context
def delete(ctx, name: str, version: int, cluster: Optional[str] = None) -> None:
    """Deletes a datastore."""
    client = Grid()
    client.delete_datastore(name=name, version=version, cluster=cluster)

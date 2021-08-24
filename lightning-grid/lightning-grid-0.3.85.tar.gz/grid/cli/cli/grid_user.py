import asyncio

import click
from grpc.aio import AioRpcError

from grid.cli import rich_click
from grid.cli.client import credentials_from_env, Grid
from grid.cli.core.team import Team
from grid.protos.grid.v1.user_pb2 import *
from grid.protos.grid.v1.user_service_pb2 import *
from grid.protos.grid.v1.user_service_pb2_grpc import *


@rich_click.group(invoke_without_command=True)
@click.pass_context
def user(ctx):
    """Show your information."""
    if ctx.invoked_subcommand is not None:
        return

    client = Grid()

    user_info = client.get_user_info()

    email = user_info['email']
    email = email if email is not None else "N/A"

    click.echo(f"Display name: {user_info['firstName']} {user_info['lastName']}")
    click.echo(f"Username    : {user_info['username']}")
    click.echo(f"Email       : {email}")

    teams = Team.get_all()
    if teams:
        click.echo("Teams:\n-")
        for t in teams:
            click.echo(f"  {t.name} - Role: {t.role}")


@user.command()
@click.argument('cluster_id', type=str)
def set_default_cluster(cluster_id: str):
    creds = credentials_from_env()

    async def f():
        async with Grid.grpc_channel() as conn:
            stub = UserServiceStub(conn)
            resp: 'GetUserResponse' = await stub.GetUser(GetUserRequest(id=creds.user_id, ))
            user: 'User' = resp.user
            user.MergeFrom(User(details=UserDetails(preferences=UserPreferences(default_cluster_id=cluster_id, ))))
            await stub.UpdateUser(UpdateUserRequest(user=user, ))

    try:
        asyncio.run(f())
        click.echo(f"default cluster_id set to {cluster_id}")
    except AioRpcError as e:
        raise click.ClickException(f"cannot set default cluster: {e.details()}")

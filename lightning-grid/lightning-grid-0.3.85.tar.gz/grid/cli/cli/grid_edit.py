import asyncio

import click
from google.protobuf.json_format import MessageToJson, Parse
from grpc.aio import AioRpcError

from grid.cli import rich_click
from grid.cli.client import Grid
from grid.protos.grid.v1.cluster_pb2 import Cluster
from grid.protos.grid.v1.cluster_service_pb2 import (
    GetClusterRequest,
    GetClusterResponse,
    UpdateClusterRequest,
    UpdateClusterResponse,
)
from grid.protos.grid.v1.cluster_service_pb2_grpc import ClusterServiceStub


@rich_click.group()
def edit() -> None:
    """Edits a resource"""
    pass


@edit.command()
@rich_click.argument('cluster', type=str)
def cluster(cluster: str):
    """Edit existing cluster"""
    async def f():
        async with Grid.grpc_channel() as conn:
            cluster_service = ClusterServiceStub(conn)
            resp: GetClusterResponse = await cluster_service.GetCluster(GetClusterRequest(id=cluster), )
            cl = resp.cluster
            before = MessageToJson(
                cl,
                including_default_value_fields=True,
            )
            after = click.edit(before)
            if after is None or after == before:
                click.echo("cluster unchanged")
                return
            cl = Cluster()
            Parse(
                text=after,
                message=cl,
            )
            resp: UpdateClusterResponse = await cluster_service.UpdateCluster(UpdateClusterRequest(cluster=cl))
            click.echo(f"{resp.cluster}")

    try:
        asyncio.run(f())
    except AioRpcError as e:
        raise click.ClickException(f"cluster {cluster}: {e.details()}")

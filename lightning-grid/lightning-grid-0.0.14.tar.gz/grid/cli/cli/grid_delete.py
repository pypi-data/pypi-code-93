import asyncio

import click
from grpc.aio import AioRpcError

from grid.cli import rich_click
from grid.cli.client import Grid
from grid.protos.grid.v1.cluster_pb2 import Cluster
from grid.protos.grid.v1.cluster_service_pb2 import DeleteClusterRequest
from grid.protos.grid.v1.cluster_service_pb2_grpc import ClusterServiceStub
from grid.protos.grid.v1.metadata_pb2 import Metadata


@rich_click.group()
def delete() -> None:
    """Deletes a Run or Experiment."""
    pass


def doublecheck(item: str):
    warning_str = click.style('WARNING!', fg='red')
    message = f"""

    {warning_str}

    Your are about to delete the {item}.
    This will delete all the associated artifacts, logs, and metadata.

    Are you sure you want to do this?

   """
    click.confirm(message, abort=True)


@delete.command()
@rich_click.argument('experiment_ids', type=str, required=True, nargs=-1)
def experiment(experiment_ids: [str]):
    doublecheck(experiment_ids)
    client = Grid()
    for experiment in experiment_ids:
        client.delete(experiment_name=experiment)


@delete.command()
@rich_click.argument('run_ids', type=str, required=True, nargs=-1)
def run(run_ids: [str]):
    doublecheck(run_ids)
    client = Grid()
    for run in run_ids:
        client.delete(run_name=run)


@delete.command()
@rich_click.argument('cluster', type=str)
def cluster(cluster: str):
    """Delete cluster"""
    async def f():
        async with Grid.grpc_channel() as conn:
            await ClusterServiceStub(conn).DeleteCluster(
                DeleteClusterRequest(cluster=Cluster(metadata=Metadata(id=cluster, )))
            )

    try:
        asyncio.run(f())
    except AioRpcError as e:
        raise click.ClickException(f"cluster {cluster}: {e.details()}")

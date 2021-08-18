import asyncio
import json
import re

import arrow
import click
from google.protobuf.json_format import MessageToJson, Parse
from grpc.aio import AioRpcError
from rich.table import Table
from rich.text import Text

from grid.cli import rich_click

# Not sure why we have this import Console
# When I import it normally from rich I have
# import issues
from grid.cli.client import credentials_from_env, Grid
from grid.cli.core.callbacks import arrow_time_callback
from grid.cli.core.formatter import Formatable, print_to_console
from grid.cli.core.logs import cluster_logs, fancy_log_writer
from grid.cli.exceptions import LogLimitExceeded
from grid.protos.grid.v1.cluster_pb2 import (
    AWSClusterDriverSpec,
    Cluster,
    CLUSTER_STATE_RUNNING,
    CLUSTER_TYPE_BYOC,
    ClusterDriver,
    ClusterSpec,
    ClusterState,
    ClusterType,
    InstanceSpec,
    KubernetesClusterDriver,
)
from grid.protos.grid.v1.cluster_service_pb2 import CreateClusterRequest, ListClustersRequest, ListClustersResponse
from grid.protos.grid.v1.cluster_service_pb2_grpc import ClusterServiceStub
from grid.protos.grid.v1.metadata_pb2 import Metadata


class ClusterList(Formatable):
    def __init__(self, clusters: [Cluster]):
        self.clusters = clusters

    def as_json(self) -> str:
        return json.dumps([
            json.loads(MessageToJson(x, including_default_value_fields=True, sort_keys=True)) for x in self.clusters
        ])

    def as_table(self) -> Table:
        table = Table("id", "name", "type", "status", "created", show_header=True, header_style="bold green")
        phases = {
            ClusterState.CLUSTER_STATE_QUEUED: Text("queued", style="bold yellow"),
            ClusterState.CLUSTER_STATE_PENDING: Text("pending", style="bold yellow"),
            ClusterState.CLUSTER_STATE_RUNNING: Text("running", style="bold green"),
            ClusterState.CLUSTER_STATE_FAILED: Text("failed", style="bold red"),
            ClusterState.CLUSTER_STATE_DELETED: Text("deleted", style="bold red"),
        }

        cluster_type_lookup = {
            ClusterType.CLUSTER_TYPE_BYOC: Text("byoc", style="bold yellow"),
            ClusterType.CLUSTER_TYPE_GLOBAL: Text("grid-cloud", style="bold green"),
        }
        for cluster in self.clusters:
            cluster: Cluster
            status = phases[cluster.status.phase]
            if cluster.spec.desired_state == ClusterState.CLUSTER_STATE_DELETED \
                    and cluster.status.phase != ClusterState.CLUSTER_STATE_DELETED:
                status = Text("terminating", style="bold red")
            table.add_row(
                cluster.metadata.id,
                cluster.metadata.name,
                cluster_type_lookup.get(cluster.spec.cluster_type, Text("unknown", style="red")),
                status,
                arrow.get(cluster.metadata.creation_timestamp.ToDatetime()).humanize(),
            )
        return table


@rich_click.group(invoke_without_command=True)
@click.pass_context
def clusters(ctx: click.Context) -> None:
    if ctx.invoked_subcommand is not None:
        return

    async def list_clusters() -> [Cluster]:
        async with Grid.grpc_channel() as conn:
            resp: 'ListClustersResponse' = await ClusterServiceStub(conn).ListClusters(
                ListClustersRequest(
                    cluster_type_not_in=[
                        ClusterType.CLUSTER_TYPE_LEGACY,
                        ClusterType.CLUSTER_TYPE_UNSPECIFIED,
                    ],
                    phase_not_in=[
                        ClusterState.CLUSTER_STATE_DELETED,
                    ]
                )
            )
            return resp.cluster

    try:
        clusters: [Cluster] = asyncio.run(list_clusters())
        print_to_console(ctx, ClusterList(clusters))
    except AioRpcError as e:
        raise click.ClickException(f"cannot list clusters: {e.details()}")


default_instance_types = [
    "g2.8xlarge",
    "g3.16xlarge",
    "g3.4xlarge",
    "g3.8xlarge",
    "g3s.xlarge",
    "g4dn.12xlarge",
    "g4dn.16xlarge",
    "g4dn.2xlarge",
    "g4dn.4xlarge",
    "g4dn.8xlarge",
    "g4dn.metal",
    "g4dn.xlarge",
    "p2.16xlarge",
    "p2.8xlarge",
    "p2.xlarge",
    "p3.16xlarge",
    "p3.2xlarge",
    "p3.8xlarge",
    "p3dn.24xlarge",
    # "p4d.24xlarge",  # currently not supported
    "t2.large",
    "t2.medium",
    "t2.xlarge",
    "t2.2xlarge",
    "t3.large",
    "t3.medium",
    "t3.xlarge",
    "t3.2xlarge",
]


def _check_cluster_name_is_valid(_ctx, _param, value):
    pattern = r"^(?!-)[a-z0-9-]{1,63}(?<!-)$"
    if not re.match(pattern, value):
        raise click.ClickException(
            f"cluster name doesn't match regex pattern {pattern}\nIn simple words, use lowercase letters, numbers, and occasional -"
        )
    return value


@clusters.command()
@click.argument('name', type=str, callback=_check_cluster_name_is_valid)
@click.option('--external-id', 'external_id', type=str, required=True)
@click.option('--role-arn', 'role_arn', type=str, required=True)
@click.option('--region', 'region', type=str, required=False, default="us-east-1")
@click.option('--instance-types', 'instance_types', type=str, required=False, default=",".join(default_instance_types))
@click.option(
    '--edit-before-creation',
    default=False,
    is_flag=True,
    help="edit the created cluster spec before submitting to API server"
)
@click.pass_context
def aws(
    ctx: click.Context,
    name: str,
    external_id: str,
    role_arn: str,
    region: str,
    instance_types: str,
    edit_before_creation: bool,
) -> None:
    creds = credentials_from_env()
    cluster = Cluster(
        metadata=Metadata(
            id=name,
            name=name,
        ),
        spec=ClusterSpec(
            desired_state=CLUSTER_STATE_RUNNING,
            user_id=creds.user_id,
            cluster_type=CLUSTER_TYPE_BYOC,
            driver=ClusterDriver(
                kubernetes=KubernetesClusterDriver(
                    aws=AWSClusterDriverSpec(
                        region=region,
                        role_arn=role_arn,
                        external_id=external_id,
                        instance_types=[InstanceSpec(name=x) for x in instance_types.split(",")]
                    ),
                ),
            )
        )
    )

    if edit_before_creation:
        before = MessageToJson(
            cluster,
            including_default_value_fields=True,
        )
        after = click.edit(before)
        if after is None or after == before:
            click.echo("cluster unchanged")
        else:
            Parse(
                text=after,
                message=cluster,
            )

    async def f():
        async with Grid.grpc_channel() as conn:
            return await ClusterServiceStub(conn).CreateCluster(CreateClusterRequest(cluster=cluster))

    try:
        resp = asyncio.run(f())
        click.echo(MessageToJson(resp.cluster))
    except AioRpcError as e:
        raise click.ClickException(f"cluster {name}: {e.details()}")


# TODO(nmiculinic): refactor this to be under `grid logs`
# Though I don't want to break existing workflows...
@clusters.command()
@click.argument('cluster_id', type=str, callback=_check_cluster_name_is_valid)
@click.option("-t", "--tail", is_flag=True, default=False, help="whether to tail log lines")
@click.option(
    "--from",
    "from_time",
    default="24 hours ago",
    help="from where are the cluster logs queried",
    callback=arrow_time_callback
)
@click.option(
    "--to",
    "to_time",
    default="0 seconds ago",
    callback=arrow_time_callback,
    help="end timestamp/relative for non-tailing requests. It's ignored for tailing ones"
)
@click.option("--limit", default=10000, help="limit the number of log lines returned")
@click.option(
    "--time-format",
    default="human",
    type=click.Choice(['human', 'iso8601'], case_sensitive=False),
    help="limit the number of log lines returned",
)
@click.option(
    "--max-per-query-limit",
    default=1000,
    help=
    "maximum number of items returns per single query. In most usecases this should not be touched, and use --limit instead"
)
def logs(cluster_id: str, time_format: str, **kwargs):
    """fetch cluster logs"""
    async def f():
        async with Grid.grpc_channel() as conn:
            await cluster_logs(
                cluster_id=cluster_id,
                cluster_service=ClusterServiceStub(conn),
                log_writer=fancy_log_writer(
                    time_format=time_format,
                    component="cluster",
                ),
                **kwargs,
            )

    try:
        asyncio.run(f())
    except AioRpcError as e:
        raise click.ClickException(f"cluster {cluster_id}: {e.details()}")
    except LogLimitExceeded:
        raise click.ClickException(
            f"=== more logs present but reached log line limit. Current limit --limit {kwargs['limit']}"
        )

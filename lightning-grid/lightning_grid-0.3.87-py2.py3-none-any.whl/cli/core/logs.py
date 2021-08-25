from typing import Callable, Optional, Tuple

import arrow
import click
from google.protobuf.timestamp_pb2 import Timestamp

from grid.cli.exceptions import LogLimitExceeded
from grid.protos.grid.v1.cluster_service_pb2 import (
    QueryClusterLogsRequest,
    QueryClusterLogsResponse,
    TailClusterLogsRequest,
    TailClusterLogsResponse,
)
from grid.protos.grid.v1.cluster_service_pb2_grpc import ClusterServiceStub
from grid.protos.grid.v1.logs_pb2 import LogEntry


def arrow_to_timestamp_pb2(timestamp: arrow.Arrow, add_nanos: int = 0) -> Timestamp:
    sol = Timestamp()
    sol.FromDatetime(timestamp.datetime)
    sol.nanos += add_nanos
    return sol


def fancy_log_writer(
    time_format: str,
    component: Optional[str] = None,
) -> Callable[[LogEntry], None]:
    def f(log_entry: LogEntry):
        timestamp = arrow.get(log_entry.timestamp.ToDatetime())
        if time_format == "human":
            timestamp_part = click.style("{:>15}".format(timestamp.humanize()), fg='green')
        elif time_format == "iso8601":
            timestamp_part = click.style(str(timestamp), fg='green')
        else:
            raise click.ClickException(f"Unknown time format: got {time_format}, valid entries: [human,iso8601]")

        component_part = click.style(component, fg='magenta')
        message_part = log_entry.message.rstrip()
        if component:
            click.echo(f"[{timestamp_part}]: {message_part}")
        else:
            click.echo(f"[{component_part}] [{timestamp_part}]: {message_part}")

    return f


async def _query_range(
    cluster_id: str,
    from_time: Timestamp,
    to_time: Timestamp,
    limit: int,
    per_query_limit: int,
    cluster_service: ClusterServiceStub,
    log_writer: Callable[[LogEntry], None],
) -> Tuple[int, Timestamp]:
    currently_fetched = 0
    while currently_fetched < limit:
        resp: QueryClusterLogsResponse = await cluster_service.QueryClusterLogs(
            QueryClusterLogsRequest(
                cluster_id=cluster_id,
                limit=min(per_query_limit, limit - currently_fetched),
                start_timestamp=from_time,
                end_timestamp=to_time,
            )
        )

        for entry in resp.entries:
            entry: LogEntry
            from_time.CopyFrom(entry.timestamp)
            from_time.nanos += 1
            log_writer(entry)

        currently_fetched += len(resp.entries)
        if len(resp.entries) < per_query_limit:
            return currently_fetched, from_time
    else:
        raise LogLimitExceeded()


async def _tail_logs(
    cluster_id: str,
    from_time: Timestamp,
    limit: int,
    cluster_service: ClusterServiceStub,
    log_writer: Callable[[LogEntry], None],
):
    if limit <= 0:
        raise LogLimitExceeded()
    async for resp in cluster_service.TailClusterLogs(
        TailClusterLogsRequest(
            cluster_id=cluster_id,
            limit=limit,
            start_timestamp=from_time,
        )
    ):
        resp: TailClusterLogsResponse
        for entry in resp.entries:
            entry: LogEntry
            limit -= 1
            log_writer(entry)
        if limit <= 0:
            raise LogLimitExceeded()


async def cluster_logs(
    cluster_id: str,
    tail: bool,
    from_time: arrow.Arrow,
    to_time: arrow.Arrow,
    limit: int,
    max_per_query_limit: int,
    cluster_service: ClusterServiceStub,
    log_writer: Callable[[LogEntry], None],
):
    per_query_limit = min(limit, max_per_query_limit)
    from_time_timestampb2 = arrow_to_timestamp_pb2(from_time)
    to_time_timestamppb2 = arrow_to_timestamp_pb2(to_time)

    currently_fetched, from_time_timestampb2 = await _query_range(
        cluster_id=cluster_id,
        from_time=from_time_timestampb2,
        to_time=to_time_timestamppb2,
        limit=limit,
        per_query_limit=per_query_limit,
        cluster_service=cluster_service,
        log_writer=log_writer,
    )
    if tail:
        await _tail_logs(
            cluster_id=cluster_id,
            from_time=from_time_timestampb2,
            limit=limit - currently_fetched,
            cluster_service=cluster_service,
            log_writer=log_writer,
        )

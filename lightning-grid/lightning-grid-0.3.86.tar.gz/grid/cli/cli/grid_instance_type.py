from collections import defaultdict
from typing import Optional

import click
from rich.console import Console

from grid import get_instance_types
from grid.cli import rich_click
from grid.cli.observables import BaseObservable
from grid.sdk import list_clusters


@rich_click.command('instance-types')
@click.option(
    '--cluster',
    'cluster_id',
    type=str,
    required=False,
    help='Cluster ID whence the instance types needs to be fetched. (Bring Your Own Cloud Customers Only).'
)
def instance_types(cluster_id: Optional[str] = None):
    if cluster_id is None:
        clusters = list_clusters()
        if len(clusters) == 0:
            raise click.ClickException('No clusters found. Raise the issue with Grid support')

        cluster_id = clusters[0].id

        if len(clusters) > 1:
            cluster_ids = [c.id for c in clusters]
            click.echo(
                f'Found multiple clusters: {", ".join(cluster_ids)}'
                f'\n\nShowing the result for {cluster_id}. Use `--cluster` argument to specify cluster'
            )
    instances = get_instance_types(cluster_id=cluster_id)
    instance_dict = defaultdict(dict)
    table = BaseObservable.create_table(columns=['Name', 'On-demand Cost', 'Spot Cost', 'CPU', 'GPU', 'Memory'])

    for i in instances:
        if i.spot:
            instance_dict[i.name]['spot_cost'] = i.hourly_cost
        else:
            instance_dict[i.name]['on_demand_cost'] = i.hourly_cost
        # these fields shouldn't be different for spot/on-demand
        instance_dict[i.name]['cpu'] = i.cpu
        instance_dict[i.name]['gpu'] = i.gpu
        instance_dict[i.name]['memory'] = i.memory

    for name, det in instance_dict.items():
        on_demand_cost = str(det.get('on_demand_cost') or "Not Available")
        spot_cost = str(det.get('spot_cost') or "Not Available")
        table.add_row(name, on_demand_cost, spot_cost, det['cpu'], det['gpu'], det['memory'])
    console = Console()
    console.print(table)

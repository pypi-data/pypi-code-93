import typer
from terminaltables import AsciiTable

from savvihub.cli.commands.utils import parse_bytes
from savvihub.cli.inputs.organization import organization_name_option
from savvihub.cli.typer import Typer, Context

cluster_app = Typer()


@cluster_app.callback()
def main():
    """
    Manage clusters
    """


@cluster_app.command(user_required=True)
def list(
    ctx: Context,
    organization_name: str = organization_name_option,
):
    """
    List custom clusters added to SavviHub
    """
    client = ctx.authenticated_client
    clusters = client.cluster_list(organization_name).clusters
    rows = []
    for cluster in clusters:
        rows.append([
            cluster.name,
            'O' if cluster.is_savvihub_managed else 'X',
            cluster.name or '-',
            cluster.kubernetes_namespace or '-',
            cluster.status.replace('-', ' ').upper(),
        ])

    table = AsciiTable([['NAME', 'SAVVIHUB-MANAGED', 'K8S MASTER ENDPOINT', 'K8S NAMESPACE', 'STATUS'], *rows])
    table.inner_column_border = False
    table.inner_heading_row_border = False
    table.inner_footing_row_border = False
    table.outer_border = False

    typer.echo(table.table)


@cluster_app.command(user_required=True)
def rename(
    ctx: Context,
    cluster_name: str = typer.Argument(..., help='Custom cluster name'),
    new_name: str = typer.Argument(..., help='A new name for the cluster'),
    organization_name: str = organization_name_option,
):
    """
    Rename a custom cluster
    """
    client = ctx.authenticated_client
    client.cluster_rename(organization_name, cluster_name, new_name)
    typer.echo(f'Successfully renamed `{cluster_name}` to `{new_name}`')


@cluster_app.command(user_required=True)
def delete(
    ctx: Context,
    cluster_name: str = typer.Argument(..., help='Custom cluster name'),
    organization_name: str = organization_name_option,
):
    """
    Delete a custom cluster
    """
    client = ctx.authenticated_client
    delete = typer.confirm(f"Are you sure you want to delete `{cluster_name}`?")
    if not delete:
        raise typer.Abort()

    client.cluster_delete(organization_name, cluster_name)
    typer.echo(f'Successfully deleted `{cluster_name}`.')


@cluster_app.command(user_required=True)
def node(
    ctx: Context,
    cluster_name: str = typer.Argument(..., help='Custom cluster name'),
    organization_name: str = organization_name_option,
):
    """
    List nodes of a custom cluster
    """
    client = ctx.authenticated_client
    nodes = client.cluster_node_list(organization_name, cluster_name).nodes

    table = AsciiTable([
        ['NODE', 'CPU', 'MEMORY', 'GPU'],
        *[[n.name,
           f'{n.cpu_allocatable - n.cpu_limits}/{n.cpu_allocatable}',
           f'{parse_bytes(n.memory_allocatable - n.memory_limits)}/{parse_bytes(n.memory_allocatable)}',
           f'{n.gpu_product_name}/{n.gpu_allocatable}'
           ] for n in nodes],
    ])
    table.inner_column_border = False
    table.inner_heading_row_border = False
    table.inner_footing_row_border = False
    table.outer_border = False

    typer.echo(table.table)

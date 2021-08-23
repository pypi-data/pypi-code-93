import inquirer
import typer
from terminaltables import AsciiTable

from savvihub.cli.exceptions import ExitException
from savvihub.cli.inputs.ssh import ssh_public_key_value_callback, ssh_key_name_callback
from savvihub.cli.typer import Typer, Context
from savvihub.common.utils import parse_time_to_ago

ssh_keys_app = Typer()


@ssh_keys_app.callback()
def main():
    """
    Manage ssh public keys
    """


@ssh_keys_app.command(user_required=True)
def add(
    ctx: Context,
    ssh_public_key_value: str = typer.Option(None, '--key-path', callback=ssh_public_key_value_callback, help='SSH key path.'),
    name: str = typer.Option(None, '--name', callback=ssh_key_name_callback, help='SSH key name.'),
):
    """
    Add a ssh public key
    """
    ctx.authenticated_client.ssh_key_add(ssh_public_key_value, name, ctx.store.get('ssh_key_filename'))
    typer.echo(f'\n'
               f'Successfully added.')


@ssh_keys_app.command(user_required=True)
def list(ctx: Context):
    """
    List ssh public keys
    """
    ssh_keys_response = ctx.authenticated_client.ssh_key_list()

    table = AsciiTable([
        ['NAME', 'FINGERPRINT', 'CREATED'],
        *[[k.name, k.fingerprint, parse_time_to_ago(k.created_dt)]
          for k in ssh_keys_response.ssh_keys],
    ])
    table.inner_column_border = False
    table.inner_heading_row_border = False
    table.inner_footing_row_border = False
    table.outer_border = False

    typer.echo(table.table)


@ssh_keys_app.command(user_required=True)
def delete(ctx: Context):
    """
    Delete a ssh public key
    """
    ssh_keys_response = ctx.authenticated_client.ssh_key_list()
    if len(ssh_keys_response.ssh_keys) == 0:
        raise ExitException('SSH public key not found.')

    ssh_key = inquirer.prompt([inquirer.List(
        'ssh_key',
        message='Select ssh public key',
        choices=[(f'{k.name} / {k.fingerprint} (created {parse_time_to_ago(k.created_dt)})', k) for k in ssh_keys_response.ssh_keys],
    )], raise_keyboard_interrupt=True).get('ssh_key')

    ctx.authenticated_client.ssh_key_delete(ssh_key.id)
    typer.echo('Successfully deleted.')

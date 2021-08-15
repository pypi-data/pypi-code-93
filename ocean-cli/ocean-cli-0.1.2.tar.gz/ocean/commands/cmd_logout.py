import click

from ocean import code
from ocean.main import pass_env


@click.command()
@pass_env
def cli(ctx):
    ctx.update_config(code.TOKEN, "")
    click.echo("Logout")

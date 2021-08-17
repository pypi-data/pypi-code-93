import click

from mahabharata.services.cli_service._commands import verses


@click.group()
def cli() -> None:
    pass


cli.add_command(verses)

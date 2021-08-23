import click

from archivr import archive


@click.command()
@click.argument('src', type=click.Path(exists=True))
def cli(src: str) -> None:
    archive(src)

if __name__=='__main__':
    cli()
import asyncio

import click

from .daemon import start


@click.command()
def main():
    asyncio.run(start())


if __name__ == '__main__':
    main()

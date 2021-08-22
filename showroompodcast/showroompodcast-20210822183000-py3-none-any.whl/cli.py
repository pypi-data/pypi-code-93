"""Console script for SHOWROOM Podcast."""

import asyncio
import sys
from pathlib import Path

import click

from showroompodcast.showroom_podcast import ShowroomPodcast


@click.command()
@click.option(
    "-f", "--file", type=click.Path(exists=True, resolve_path=True, path_type=Path), default=Path("config.yml")
)
def showroom_podcast(file):
    """Console script for SHOWROOM Podcast."""
    podcast = ShowroomPodcast(path_to_configuraion=file)
    try:
        podcast.run()
    except (KeyboardInterrupt, asyncio.CancelledError):
        sys.exit(130)

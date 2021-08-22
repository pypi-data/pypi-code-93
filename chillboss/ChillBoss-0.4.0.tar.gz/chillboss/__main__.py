"""Run ChillBoss as a module."""

import logging

import click
from emoji import emojize
from pyfiglet import figlet_format

from chillboss import __version__
from chillboss.mouse import Pointer

logger: logging.Logger = logging.getLogger("chillboss")


@click.command()
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Flag argument which sets the log level to Debug.",
)
@click.option(
    "-m",
    "--movement",
    type=click.Choice(["random", "square"], case_sensitive=False),
    default="random",
    help="`random` and `square` movements are accepted. Default set to `random`",
)
@click.option(
    "-l",
    "--length",
    type=int,
    default=None,
    help="Accepted for `square` type of movement. Default set to `None`.",
)
@click.option(
    "-s",
    "--sleeptime",
    type=int,
    default=30,
    help="Time to be taken till next movement. Default set to 30 seconds.",
)
@click.option(
    "-mt",
    "--motiontime",
    type=int,
    default=0,
    help="Time consumption of pointer to move from present coordinates to the next coordinates. "
    "Default set to 0 seconds.",
)
def chill(
    motiontime: int, sleeptime: int, length: int, movement: str, verbose: bool
) -> None:
    """
    Welcome to ChillBoss. We hope you are having a chill life.
    """
    if verbose:
        logger.setLevel(logging.DEBUG)
    pointer = Pointer(
        movement=movement, length=length, sleep_time=sleeptime, motion_time=motiontime
    )
    print(figlet_format("ChillBoss"))
    print(f"Version: {__version__}")
    pointer.move_the_mouse_pointer()
    print(emojize("\nThanks for using ChillBoss :red_heart:", variant="emoji_type"))


if __name__ == "__main__":
    chill()

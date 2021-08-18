import os
import platform
import sys
from datetime import datetime
from rich import print
from rich.tree import Tree
from rich.panel import Panel
from rich.columns import Columns
from rich.text import Text

CURSOR_UP_ONE = "\x1b[1A"
ERASE_LINE = "\x1b[2K"


def print_command_header(command: str):
    """Global header

    Args:
        command (str): Executed command
    """
    print(
        Panel(
            Columns(
                [
                    Text("Made By Tanguy Cavagna with 💖", style="italic"),
                    Text(
                        datetime.now().strftime("%Y-%m-%d, %H:%M:%S"),
                        justify="right",
                        style="italic",
                    ),
                ],
                expand=True,
                title="[bold bright_white]HES-SO[/bold bright_white] - [bold red1]HEPIA[/bold red1]",
            ),
            border_style="bright_white",
            title=f"Command: [orange_red1]{command}[/orange_red1]",
            title_align="left",
        )
    )


def clr_scr():
    """Clear screen on all os"""
    if platform.system().lower() == "windows":
        os.system("cls")
    else:
        os.system("clear")


def del_last_line():
    """Delete the last console line"""
    sys.stdout.write(CURSOR_UP_ONE)
    sys.stdout.write(ERASE_LINE)

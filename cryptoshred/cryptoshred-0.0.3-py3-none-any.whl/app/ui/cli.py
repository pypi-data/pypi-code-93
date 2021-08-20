import typer
import logging
from rich.console import Console
from rich.logging import RichHandler
from typing import List

from cryptoshred.app.business.cli import get_key_backend

from .decrypt import app as decrypt_app
from .encrypt import app as encrypt_app
from .map import app as mapping_app

console = Console()
app = typer.Typer()

FORMAT = "%(message)s"


@app.callback()
def main(
    ctx: typer.Context,
    verbose: List[bool] = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Output more details on what is happening. Use multiple times for more details.",
    ),
    profile: str = typer.Option(
        "default",
        "--profile",
        "-p",
        help="The profile to use for the command that is about to run.",
    ),
) -> None:
    level = "WARNING"
    if len(verbose) == 1:
        level = "INFO"
    if len(verbose) >= 2:
        level = "DEBUG"

    logging.basicConfig(
        level=level, format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
    )

    ctx.obj = {"key_backend": get_key_backend(profile=profile)}


app.add_typer(decrypt_app, name="decrypt")
app.add_typer(encrypt_app, name="encrypt")
app.add_typer(mapping_app, name="map")

typer_click_object = typer.main.get_command(app)

if __name__ == "__main__":
    app()

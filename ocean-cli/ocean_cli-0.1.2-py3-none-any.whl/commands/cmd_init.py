import click
import os

from ocean import code
from ocean.main import Environment


@click.command()
def cli():
    ctx = Environment(load=False)

    # make .oceanrc on home-dir
    if not ctx.config_path.exists():
        ctx.config_path.parent.mkdir(exist_ok=True)
        ctx.config_path.touch()

    url = (
        "http://"
        + os.environ["OCEAN_BACKEND_SVC_SERVICE_HOST"]
        + ":"
        + os.environ["OCEAN_BACKEND_SVC_SERVICE_PORT"]
    )

    # save env
    ctx.update_config(code.OCEAN_URL, url)
    ctx.update_config("presets", [])

    click.echo("Setup Success.")

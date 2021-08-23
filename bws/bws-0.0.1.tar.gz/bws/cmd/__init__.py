import click
import os
from .base import create_app, create_project


@click.group(help="Builer Web Services.")
def bws_cli():
    pass


@bws_cli.command()
@click.option(
        "--project",
        "project",
        default=os.getcwd(),
        help="Direccion del proyecto.",
)
@click.option(
        "--app",
        "app",
        default="main",
        help="Nombre de la app default",
)
def init(project, app):
    create_project(project, app)
    


def callback(ctx, param, value):
    print(ctx, param, value)
    if not value and param:
        ctx.abort()

@bws_cli.command()
@click.option(
        "--dir",
        default=os.getcwd() + "/app",
        help="Nombre de la app default",
)
@click.option(
        "--name",
        # is_flag=True,
        # callback=callback, 
        # expose_value="",
        prompt='Escribe el nomnbre de la aplicación',
        help="Nombre de la app",
)
def add_app(dir, name):
    if not name:
        print("name is required")
        return
    create_app(dir, name)

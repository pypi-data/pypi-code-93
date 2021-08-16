import logging

import click

from tktl.commands.init import init_project

_logger = logging.getLogger("root")


@click.command(help="Creates project scaffolding")
@click.option(
    "--name", help="Name of the project", default="tktl-serving", required=True
)
@click.option(
    "--path", help="Directory where the new project will be created", required=False
)
def init(path: str, name: str) -> None:
    """Creates a new project with the necessary scaffolding.

    Creates the supporting files needed. The directory structure of a new
    project , and the files within it will look like this:

        .dockerignore
        .gitattributes
        .gitignore
        .buildfile
        README.md
        assets              # Where your ML models and test data live
        requirements.txt    # User-specified requirements
        src                 # Source code for endpoint definitions
        tests               # User-specified tests
        tktl.yaml           # Taktile configuration options

    """
    init_project(path=path, name=name)

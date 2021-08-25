# type: ignore

import asyncio
import sys

import click
from PyQt5 import QtWidgets

from n_edit import editor, execution, model


def make_editor_command(library: model.NodeLibrary):
    @click.command()
    @click.argument("file-name", type=click.types.Path(dir_okay=False, writable=True))
    def edit(file_name: str):
        app = QtWidgets.QApplication(sys.argv)

        window = editor.EditorWindow(file_name, library)
        window.show()

        sys.exit(app.exec_())

    return edit


def make_run_command(library: model.NodeLibrary, executor: execution.NodeExecutor):
    @click.command()
    @click.argument("file-name", type=click.types.Path(dir_okay=False, writable=True))
    def run(file_name: str):
        graph = model.Graph(library)
        graph.load_file(file_name)
        asyncio.run(execution.Run(graph, executor).run())

    return run


def make_cli(library: model.NodeLibrary, executor: execution.NodeExecutor):
    @click.group()
    def cli():
        pass

    cli.add_command(make_editor_command(library), name="edit")
    cli.add_command(make_run_command(library, executor), name="run")
    return cli

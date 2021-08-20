"""Console script for xepmts_endpoints."""
import sys

import click
from xepmts_server import make_app
from werkzeug.serving import run_simple
from flask.cli import with_appcontext


@click.group()
def main():
    """Console script for xepmts_endpoints."""
    click.echo("Replace this message by putting your code into "
               "xepmts_endpoints.cli.main")
    click.echo("See click documentation at https://click.palletsprojects.com/")
    return 0


@main.command()
@with_appcontext
def run(address='0.0.0.0', port=5000):
    app = make_app()
    run_simple(address, port, app,
                use_reloader=False, use_debugger=False, use_evalex=False)

@main.command()
@with_appcontext
def debug(address='0.0.0.0', port=5000):
    app = make_app(debug=True)
    run_simple(address, port, app,
                use_reloader=True, use_debugger=True, use_evalex=True)


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover

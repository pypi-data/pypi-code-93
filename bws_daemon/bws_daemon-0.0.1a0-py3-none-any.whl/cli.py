from __future__ import annotations

import click
from flask.cli import with_appcontext
from bws_daemon.manager import _Manager


def common_options(f):
    f = click.option(
        "--suppress",
        "verbose",
        flag_value=False,
        default=True,
        help="Do not show verbose outputs.",
    )(f)
    return with_appcontext(f)


@click.group(help="Manage the scheduled deamons. Author: @jad21: Jose Angel Delgado.")
def bws_daemon_cli():
    pass


@bws_daemon_cli.command()
@common_options
@click.argument("name")
def start(verbose, name):
    c = _Manager(verbose=verbose)
    c.start_daemon(name)


@bws_daemon_cli.command()
@common_options
@click.argument("name")
def stop(verbose, name):
    c = _Manager(verbose=verbose)
    c.stop_daemon(name)


@bws_daemon_cli.command()
@common_options
def start_all(verbose):
    c = _Manager(verbose=verbose)
    c.start_daemons()


@bws_daemon_cli.command()
@common_options
def stop_all(verbose):
    c = _Manager(verbose=verbose)
    c.stop_daemons()


@bws_daemon_cli.command()
@common_options
@click.argument("name")
def restart(verbose, name):
    c = _Manager(verbose=verbose)
    c.stop_daemon(name)
    c.start_daemon(name)


@bws_daemon_cli.command()
@common_options
@click.argument("name")
def status(verbose, name):
    c = _Manager(verbose=verbose)
    c.status_daemon(name)


@bws_daemon_cli.command()
@common_options
def list(verbose):
    c = _Manager(verbose=verbose)
    c.show_daemons()

@bws_daemon_cli.command()
@common_options
@click.argument("name")
def log(verbose, name):
    c = _Manager(verbose=verbose)
    c.log_daemon(name)


@bws_daemon_cli.command()
@common_options
@click.argument("name")
def clear_log(verbose, name):
    c = _Manager(verbose=verbose)
    c.clear_log_daemon(name)


@bws_daemon_cli.command()
@common_options
def clear_log_all(verbose):
    c = _Manager(verbose=verbose)
    c.clear_log_daemons()


starts = start_all
stops = stop_all
clear_logs = clear_log_all

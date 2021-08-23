import os

import click


@click.group(name="set")
def config_set_group():
    """Set a durable parameter."""


@config_set_group.command(name="rae")
@click.argument("rae")
def config_set_rae(rae):
    # todo any error checking?
    os.environ["RAE"] = rae


@config_set_group.command(name="esn")
@click.argument("esn")
def config_set_esn(esn):
    # todo interactive?
    # todo any error checking?
    os.environ["ESN"] = esn

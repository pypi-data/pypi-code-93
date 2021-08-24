"""This module contains the midas command line interface 2.0."""
import logging
import os

import click
from midas.scenario import Configurator
from midas.tools import analysis, config
from midas.util.logging_util import setup_logging


@click.group(invoke_without_command=True)
@click.option(
    "--log",
    "-l",
    default="DEBUG",
    help="Set the log level (DEBUG|INFO|WARN|ERROR)",
)
@click.option(
    "--inipath",
    "-i",
    default=None,
    help="Specify the path to the midas.ini to use.",
)
@click.option(
    "--datapath", "-d", default=None, help="Specify the path to the datasets."
)
@click.option(
    "--autocfg",
    "-a",
    is_flag=True,
    help=(
        "Skip ini dialog and apply defaults or use inipath and datapath"
        " if provided with this command."
    ),
)
@click.pass_context
def cli(ctx, log, inipath, datapath, autocfg):
    ctx.ensure_object(dict)
    ctx.obj["log"] = log
    setup_logging(log, "midas")

    configurator = Configurator(inipath, datapath, autocfg)

    # midas_cfg = config.check_config(inipath)
    # if midas_cfg is None:
    #     config.dialog(inipath, datapath, autocfg)
    #     midas_cfg = config.check_config(inipath)
    ctx.obj["inipath"] = inipath
    ctx.obj["datapath"] = datapath
    ctx.obj["autocfg"] = autocfg
    ctx.obj["configurator"] = configurator


@cli.command()
@click.option(
    "--config",
    "-c",
    multiple=True,
    help=(
        "Provide a custom (scenario-)config file. Providing a scenario"
        " name is still required "
    ),
)
@click.option(
    "--no-db",
    "-nd",
    "no_db",
    is_flag=True,
    help=(
        "Disable the database. Default behavior is to use the settings"
        " of the scenario file."
    ),
)
@click.option(
    "--db-file",
    "-df",
    "db_file",
    help=(
        "Specify a database file. Temporarily overwrites the scenario "
        "file settings. The -nd flag is ignored."
    ),
)
@click.option(
    "--scenario-name",
    "-n",
    "scenario_name",
    default="demo",
    help="The name of the scenario to run.",
)
@click.option(
    "--silent",
    "-q",
    is_flag=True,
    help="Pass the silent flag to mosaik to suppress mosaik output",
)
@click.option(
    "--port",
    "-p",
    default=5555,
    type=int,
    help="Specify the port for mosaik.",
)
@click.option(
    "--no-rng",
    "-nr",
    "norng",
    is_flag=True,
    help="Globally disable random number generator in the simulation.",
)
@click.option(
    "--seed", "-s", type=int, help="Set a positive integer as random seed."
)
@click.option(
    "--end",
    "-e",
    default=None,
    type=int,
    help="Specify the number of simulation steps.",
)
@click.pass_context
def run(ctx, **kwargs):
    main_run(ctx, **kwargs)


@cli.command()
@click.option(
    "--db-file",
    "-df",
    "db_file",
    default=None,
    help=(
        "Specify the database file for analysis. db_file needs to "
        "point to a mosaikhdf5 database file. Midas will look in the "
        "default _outputs folder if the database was not directly "
        "found (e.g. specifying only the filename without path is "
        "sufficient if your database file is in that very folder)."
    ),
)
@click.option(
    "--output-folder",
    "-of",
    "output_folder",
    default=None,
    help=(
        "Specify the folder where to store the analysis results. "
        "If not provided, the default output folder is used."
    ),
)
@click.option(
    "--db-style",
    "-ds",
    "db_style",
    default="mosaik",
    help=(
        "Set the database style. Default is mosaik, which assumes a "
        "database created with mosaikHDF5. The other option is midas, "
        "which uses the new midasHDF5 database created with pytables."
    ),
)
@click.pass_context
def analyze(ctx, **kwargs):

    main_analyze(ctx, **kwargs)


def main_run(ctx, **kwargs):
    """The run function of midas CLI."""
    setup_logging(
        kwargs.get("log", "DEBUG"),
        kwargs.get("db_file", kwargs.get("scenario_name", "midas")),
    )
    log = logging.getLogger("midasctl")
    log.info("This is the MIDAS control CLI. Enjoy! :)")

    params = dict()
    end = kwargs.get("end", None)
    if end is not None:
        params["end"] = end

    name = kwargs.get("scenario_name", "demo")
    if name == "demo":
        name = "midasmv"
        params.setdefault("end", 1 * 12 * 60 * 60)
        log.info("Will run the demo scenario %s.", name)

    db_file = kwargs.get("db_file", None)
    if db_file is not None:
        params["with_db"] = True
        params["mosaikdb_params"] = {"filename": f"{db_file}.hdf5"}
    else:
        params["with_db"] = not kwargs.get("no_db", False)

    seed = kwargs.get("seed", None)
    if seed is not None:
        try:
            seed = abs(int(seed))
        except ValueError:
            log.info("Seed %s is not an integer. Seed will be random, then!")
            seed = "random"
        params["seed"] = seed
    params["deny_rng"] = kwargs.get("norng", False)

    port = kwargs.get("port", 5555)
    try:
        port = int(port)
    except ValueError:
        log.info("Port %s is not an integer. Using default port 5555.")
        port = 5555

    params["mosaik_params"] = {"addr": ("127.0.0.1", port)}

    custom_cfg = kwargs.get("config", tuple())
    if len(custom_cfg) > 0:
        custom_cfg = [os.path.abspath(ccfg) for ccfg in custom_cfg]
    else:
        custom_cfg = None
    params["silent"] = kwargs.get("silent", False)

    log.debug("Creating the configurator.")
    cfg = ctx.obj["configurator"]

    log.debug("Calling configure of the configurator.")
    scenario = cfg.configure(name, params, custom_cfg)

    if scenario:
        log.debug("Calling run of the configurator.")
        cfg.run()
    else:
        log.info("Scenario configuration failed.")
        click.echo(
            "Scenario configuration failed. See log file for more infos."
        )


def main_analyze(ctx, **kwargs):
    """The analyze function of midas CLI."""
    name = kwargs.get("db_file", None)
    midas_cfg = ctx.obj["configurator"].midascfg
    if name is None:
        click.echo("No file provided. Terminating!")
        return

    if not name.endswith(".hdf5"):
        db_file = f"{name}.hdf5"
        name = os.path.split(name)[-1]
    else:
        db_file = name
        name = os.path.split(name)[-1][:-5]

    if not os.path.isfile(db_file):
        db_file = os.path.join(midas_cfg["PATHS"]["output_prefix"], db_file)

    if not os.path.isfile(db_file):
        click.echo(
            f"Could not find database at {kwargs.get('db_file')}. "
            "Terminating!"
        )
        return

    db_file = os.path.abspath(db_file)

    output_folder = kwargs.get("output_folder", None)
    if output_folder is None:
        output_folder = midas_cfg["PATHS"]["output_prefix"]

    output_folder = os.path.abspath(output_folder)
    if not output_folder.endswith(name):
        output_folder = os.path.join(output_folder, name)

    os.makedirs(output_folder, exist_ok=True)

    click.echo(f'Reading database at "{db_file}".')
    click.echo(f'Saving results to "{output_folder}".')

    analysis.analyze(
        name, db_file, output_folder, kwargs.get("db_style", "mosaik")
    )


if __name__ == "__main__":
    cli(obj=dict())

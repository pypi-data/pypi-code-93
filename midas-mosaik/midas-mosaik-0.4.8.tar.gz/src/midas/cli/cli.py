"""This module contains the midas command line interface."""
import logging
import warnings

import click
import os

from midas.scenario import Configurator
from midas.util.logging_util import setup_logging


@click.command()
@click.option(
    "--config",
    "-c",
    help="Provide a custom config file. Providing a scenario name is "
    "still required.",
)
@click.option(
    "--with-db",
    "-d",
    "with_db",
    is_flag=True,
    help="Use a mosaikhdf5 database to log outputs.",
)
@click.option(
    "--db-file",
    "-df",
    "db_file",
    help="Specify a mosaikhdf5 database file. " "The -d flag is ignored.",
)
@click.option(
    "--scenario-name",
    "-n",
    "scenario_name",
    default="demo",
    help="The name of the scenario to run.",
)
@click.option(
    "--silent", "-q", is_flag=True, help="Suppress output from mosaik."
)
@click.option("--port", "-p", default=5555, help="Specify the port for mosaik")
@click.option(
    "--log",
    "-l",
    default="DEBUG",
    help="Set the log level (DEBUG|INFO|WARN|ERROR)",
)
@click.option(
    "--no-rng",
    "-r",
    "norng",
    is_flag=True,
    help="Globally disable random number generator in the simulation",
)
@click.option("--seed", "-s", help="Set a positive integer as random seed.")
@click.option(
    "--version", "-v", is_flag=True, help="Print the program version."
)
@click.option(
    "--autocfg", is_flag=True, help="Skip ini dialog and apply defaults."
)
@click.option(
    "--inipath", default=None, help="Specifiy the path to the ini to use."
)
def cli(**kwargs):
    """Command line interface for midas."""
    main(**kwargs)


def main(**kwargs):
    """The main function of the midas CLI."""
    click.echo("midascli is now deprecated. Use midasctl (--help) instead.")
    vers_no = _get_version()
    if kwargs.get("version", False):
        click.echo(vers_no)
        return

    setup_logging(kwargs.get("log", "DEBUG"), kwargs.get("db_file", "midas"))
    logger = logging.getLogger("midas.cli")
    logger.info(
        "This is the MIDAS command line interface version %s. Enjoy! :)",
        vers_no,
    )

    params = dict()

    scenario_name = kwargs.get("scenario_name", "demo")
    if scenario_name == "demo":
        scenario_name = "midasmv"
        params["end"] = 1 * 12 * 60 * 60
        logger.info("Will run the demo scenario %s.", scenario_name)

    db_file = kwargs.get("db_file", None)
    if db_file is not None:
        params["with_db"] = True
        params["mosaikdb_params"] = {"filename": f"{db_file}.hdf5"}
    else:
        params["with_db"] = kwargs.get("with_db", True)

    seed = kwargs.get("seed", None)
    if seed is not None:
        try:
            seed = int(seed)
        except ValueError:
            msg = f"Seed {seed} is not an integer. Seed will be random, then!"
            warnings.warn(msg)
            seed = "random"
        params["seed"] = seed

    params["deny_rng"] = kwargs.get("norng", False)
    port = kwargs.get("port", 5555)
    try:
        port = int(port)
    except ValueError:
        warnings.warn(
            f"Port {port} is not an integer. " "Using default port 5555."
        )
        port = 5555

    params.setdefault("mosaik_params", {"addr": ("127.0.0.1", port)})

    custom_cfg = kwargs.get("config", None)
    if custom_cfg is not None:
        if isinstance(custom_cfg, list):
            custom_cfg = [os.path.abspath(ccfg) for ccfg in custom_cfg]
        else:
            custom_cfg = [os.path.abspath(custom_cfg)]

    # print(params)
    params["silent"] = kwargs.get("silent", False)

    logger.debug("Creating the configurator")

    autocfg = kwargs.get("autocfg", False)
    inipath = kwargs.get("inipath", None)

    cfg = Configurator(inipath=inipath, autocfg=autocfg)
    logger.debug("Calling configure of the configurator.")
    scenario = cfg.configure(scenario_name, params, custom_cfg)

    if scenario:
        logger.debug("Calling run of the configurator.")
        cfg.run()
    else:
        logger.info("Scenario configuration failed.")


def _get_version():
    try:
        v_path = os.path.abspath(
            os.path.join(__file__, "..", "..", "..", "..", "VERSION")
        )
        with open(v_path) as v_file:
            version = v_file.readline().strip()
    except FileNotFoundError:
        version = "1.0.0"
    return version


if __name__ == "__main__":
    main(scenario_name="midasmv_der", with_db=True)
    # main(scenario_name="sburban0", with_db=True)
    # main(scenario_name="four_bus_der", with_db=True, port=5777)
    # main(
    #     config="src/midas/adapter/qmarket/qmarket.yml",
    #     scenario_name="qmarket",
    #     with_db=True,
    #     db_file="pyrate",
    # )
    # main(
    #     config="src/midas/adapter/mango/blackstart.yml",
    #     scenario_name="blackstart",
    #     with_db=True,
    # )

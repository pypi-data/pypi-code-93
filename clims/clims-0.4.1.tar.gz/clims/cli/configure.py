import click
import json
from pathlib import Path

config_dir = Path.home() / ".local" / "etc"
config_file = config_dir / "clims_config.json"


@click.command()
@click.option(
    "--species-path",
    type=click.Path(exists=True),
    help="Path to the aims species_defaults folder.",
)
@click.option(
    "--aims-executable",
    type=click.Path(exists=True),
    help="Path to the the aims executable.",
)
@click.option(
    "--submission-header",
    default=None,
    type=click.File(),
    help="File containing a submission header for queing systems.",
)
@click.option(
    "--mpi-command", default=None, type=str, help="MPI run command, e.g. 'mpirun -n 4'."
)
@click.option(
    "--output-name", default=None, type=str, help="Name of the aims output file."
)
@click.option("--error-name", default=None, type=str, help="Name of the error file.")
@click.option(
    "--submit-command",
    default=None,
    type=str,
    help="Command to submit a calculation to queing system.",
)
@click.option("--show", is_flag=True, help="Show the content of the configure file.")
def clims_configure(
    species_path,
    aims_executable,
    mpi_command,
    output_name,
    error_name,
    submission_header,
    submit_command,
    show,
):
    """
    Configure clims standard parameters. This is mandatory for some of the cli tools,
    e.g. `clims-prepare_run` , etc.
    """

    try:
        with open(config_file) as config_json:
            config = json.load(config_json)
    except FileNotFoundError:
        config = {}
        if not config_dir.exists():
            config_dir.mkdir(parents=True)

    if show:
        print("-- Configuration file:")
        for key, value in config.items():
            print(f"{key:20} : {value}")
        return

    # First print the current config file

    if species_path:
        s_path = Path(species_path)
        config["species_path"] = s_path.as_posix()

    if aims_executable:
        a_path = Path(aims_executable)
        config["aims_executable"] = a_path.as_posix()

    if submission_header:
        sh_text = submission_header.read()
        config["submission_header"] = sh_text

    if output_name:
        config["output_name"] = output_name

    if error_name:
        config["error_name"] = error_name

    if mpi_command:
        config["mpi_command"] = mpi_command

    if submit_command:
        config["submit_command"] = submit_command

    with open(config_file, "w") as config_json:
        json.dump(config, config_json)


def get_config_value(key):
    """Return the `value` of `key` of `config_json` file."""

    try:
        with open(config_file) as config_json:
            config = json.load(config_json)
            value = config[key]
            return value
    except FileNotFoundError:
        print("A config value was requested. Please configure clims first!")
        print('Get more information with: "clims-configure --help"')
        raise
    except KeyError:
        print("Default {key} is not set, yet.")
        print(f'Please set with: "clims-configure --{key.replace("_","-")} <...>"')
        raise

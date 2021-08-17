import logging
import sys
from functools import wraps
from pathlib import Path
from typing import Mapping

import click
import toml
from click.exceptions import Exit
from dendrodict import DottedDeepDict
from exit_codes import ExitCode

import godkjenn.commands
import godkjenn.comparators.exact
from godkjenn import __version__
from godkjenn.diff_selector import DiffSelector
from godkjenn.vaults.fs_vault import FSVault

log = logging.getLogger(__name__)


@click.group()
@click.option(
    "--cwd",
    "-C",
    type=click.Path(exists=True, readable=True, file_okay=False),
    default=Path("."),
    help="Directory from which to start search for the data-dir.",
)
@click.option(
    "--data-dir",
    "-d",
    default=".godkjenn",
    help="Directory (relative to --cwd) containing the vault.",
)
@click.option(
    "--init/--no-init", default=True, help="Whether to initialize a godkjenn data directory if one is not found."
)
@click.option(
    "--verbosity",
    default="WARNING",
    help="The logging level to use.",
    type=click.Choice(
        [name for lvl, name in sorted(logging._levelToName.items()) if lvl > 0],
        case_sensitive=True,
    ),
)
@click.version_option(version=__version__)
@click.pass_context
def cli(ctx, cwd, data_dir, init, verbosity):
    """Command-line interface for godkjenn."""
    logging_level = getattr(logging, verbosity)
    logging.basicConfig(level=logging_level)

    ctx.ensure_object(dict)
    ctx.obj.update(
        {
            "cwd": Path(cwd),
            "data-dir": data_dir,
            "allow-init": init,
        }
    )


def access_data_dir(initialize_data_directory=False):
    """Decorator that unpacks the vault and config from the group context.

    This let's the decorated subcommand have a simpler, more natural signature.
    """

    def decorator(f):
        @wraps(f)
        def wrapper(params, *args, **kwargs):
            cwd = params["cwd"]
            data_dir = params["data-dir"]
            init = params["allow-init"] and initialize_data_directory

            godkjenn_dir = _ensure_godkjenn_dir(data_dir, cwd, init)

            vault = FSVault(godkjenn_dir / "vault")

            config = _load_config(godkjenn_dir)

            return f(vault, config, *args, **kwargs)

        return wrapper

    return decorator


@cli.command()
@click.argument("test_id")
@click.pass_obj
@access_data_dir()
def accept(vault, config, test_id):
    """Accept the current received data for a test."""
    try:
        vault.accept(test_id)
    except KeyError:
        log.error("No received data for {}".format(test_id))
        return ExitCode.DATA_ERR

    return ExitCode.OK


@cli.command()
@click.pass_obj
@access_data_dir()
def accept_all(vault, config):
    """Accept all received data for a configuration/root directory."""
    for test_id in vault.ids():
        try:
            vault.accept(test_id)
        except KeyError:
            # This just means there isn't any received data for the ID, just accepted.
            pass

    return ExitCode.OK


@cli.command()
@click.argument("test_id")
@click.argument("destination", type=click.File(mode="wb"))
@click.pass_obj
@access_data_dir()
def accepted(vault, config, test_id, destination):
    """Get accepted data for a test."""
    try:
        artifact = vault.accepted(test_id)
    except KeyError:
        print(f"No accepted data for id {test_id}", file=sys.stderr)
        return ExitCode.DATA_ERR

    destination.write(artifact.path.read_bytes())

    return ExitCode.OK


@cli.command()
@click.argument("test_id")
@click.argument("data_source", type=click.File(mode="rb"))
@click.argument("mime_type")
# TODO: Add encoding
@click.pass_obj
@access_data_dir(initialize_data_directory=True)
def receive(vault, config, test_id, data_source, mime_type):
    """Receive new data for a test."""
    data = data_source.read()
    vault.receive(test_id, data, mime_type, None)

    return ExitCode.OK


@cli.command()
@click.argument("test_id")
@click.argument("destination", type=click.File(mode="wb"))
@click.pass_obj
@access_data_dir()
def received(vault, config, test_id, destination):
    """Get received data for a test."""
    try:
        artifact = vault.received(test_id)
    except KeyError:
        print(f"No received data for {test_id}", file=sys.stderr)
        return ExitCode.DATA_ERR

    destination.write(artifact.path.read_bytes())

    return ExitCode.OK


@cli.command()
@click.argument("test_id")
@click.option("-f", "--fallback", help="Only use the fallback differ, ignoring differ configs.", is_flag=True)
@click.pass_obj
@access_data_dir()
def diff(vault, config, test_id, fallback):
    """Get diff between accepted and received data for a test."""
    diff_selector = _get_diff_selector(fallback, config)

    try:
        godkjenn.commands.diff(vault, test_id, diff_selector)
    except KeyError as exc:
        log.error("%s", str(exc))
        return ExitCode.DATA_ERR

    return ExitCode.OK


@cli.command()
@click.option("-j", "--as-json", is_flag=True)
@click.option(
    "-a",
    "--show-all",
    is_flag=True,
    help="Whether to show all test-ids. By default up-to-date entries will not be shown.",
)
@click.pass_obj
@access_data_dir()
def status(vault, config, as_json, show_all):
    """Print status of godkjenn vault"""
    godkjenn.commands.status(vault, as_json=as_json, include_up_to_date=show_all)
    return ExitCode.OK


@cli.command()
@click.option("-f", "--fallback", help="Only use the fallback differ, ignoring differ configs.", is_flag=True)
@click.pass_obj
@access_data_dir()
def review(vault, config: Mapping, fallback):
    "View each 'mismatch' test-id with a diff/merge tool."
    diff_selector = _get_diff_selector(fallback, config)

    godkjenn.commands.review(vault, diff_selector)
    return ExitCode.OK


def _get_diff_selector(fallback, config) -> DiffSelector:
    """Build the DiffSelector based on configuration and options.

    Args:
        fallback: Whether we should use only the fallback differs (i.e. ignore configuration)
        config: The godkjenn config dict.
    """
    if fallback:
        diff_selector = DiffSelector({}, None)
    else:
        default_command_template = config.get("differs.default_command")
        command_templates = config.get("differs.mime_types", {})

        if (not command_templates) and (default_command_template is None):
            log.warning("No review tools configured. Fallback differs will be used.")

        diff_selector = DiffSelector(command_templates, default_command_template)
    return diff_selector


def _find_dominating(filename: str, start_path: Path):
    """Look for `filename` in `start_path` or any of its ancestor directories.

    Args:
        filename: The filename to look for
        start_path: The directory in which to start the search

    Returns: The dominating path

    Raises:
        FileNotFoundError: The dominating directory is not found.
    """
    path = start_path.absolute()
    if path.is_file():
        path = path.parent

    while True:
        if (path / filename).exists():
            return path
        if path == path.parent:
            break
        path = path.parent

    raise FileNotFoundError(f'No file named "{filename}" dominating {start_path}')


def _ensure_godkjenn_dir(data_dir, search_root, init_allowed):
    "Locate the godkjenn data directory or, if allowed, create it."
    try:
        godkjenn_dir = _find_dominating(data_dir, Path(search_root)) / data_dir
        log.info("Found data directory: %s", godkjenn_dir)
    except FileNotFoundError:
        log.info("No dominating data directory found.")

        if not init_allowed:
            log.error("No data directory found.")
            raise Exit(ExitCode.OS_FILE)

        godkjenn_dir = search_root / data_dir
        log.info("Creating godkjenn data directory: %s", godkjenn_dir)
        assert not godkjenn_dir.exists()
        godkjenn_dir.mkdir()
        config_file = godkjenn_dir / "config.toml"
        config_file.write_text("[godkjenn]")

    return godkjenn_dir


def _load_config(godkjenn_dir) -> Mapping:
    "Load config if available, returning it or an empty config."
    config = {}
    try:
        config_text = (godkjenn_dir / "config.toml").read_text()
        log.info("Loading config file: %s", godkjenn_dir / "config.toml")
        config = toml.loads(config_text)
    except OSError as err:
        log.info("No config file: %s", err)
    except toml.TomlDecodeError as err:
        log.error("Error loading config: %s", err)
        raise Exit(ExitCode.DATA_ERR)

    config = config.get("godkjenn", {})

    log.info("Config: %s", config)
    return DottedDeepDict(config)


def main(argv=None, standalone_mode=True):
    return cli(argv, standalone_mode=standalone_mode)


if __name__ == "__main__":
    sys.exit(main())

from typing import Any, Dict, io

import click
import yaml

DISK_SIZE_ERROR_MSG = "Invalid disk size, should be greater than 100Gb"


def validate_config(cfg: Dict[str, Any]) -> None:
    """
    Validates Grid config.

    Parameters
    ----------
    cfg: Dict[str, Any]
        Dictionary representing a Grid config
    """
    disk_size = cfg['compute']['train'].get('disk_size')
    if disk_size is not None and disk_size < 100:
        raise click.ClickException(DISK_SIZE_ERROR_MSG)


def read_config(value: io.TextIO):
    """
    Parameters
    ----------
    value:
        A TextIO object that has `.read()` defined for it
    """
    grid_config = value
    if grid_config:
        #  Loads the YML file as passed by the
        #  user.
        try:
            grid_config = yaml.safe_load(value.read())
            if not isinstance(grid_config, dict):
                raise Exception("Unexpected file structure")
        except Exception as e:
            raise click.BadParameter(f'Could not load your YAML config file: {e}')

        #  Adds required structure to the base
        #  YML file, if that structure isn't there.
        if 'compute' not in grid_config:
            grid_config['compute'] = {}
        if 'train' not in grid_config['compute']:
            grid_config['compute']['train'] = {}
    return grid_config


def read_config_callback(ctx, param, value):
    """
    Click callback that reads value from the config file and fix
    the structure if it doesn't exist.
    """
    return read_config(value)


def validate_disk_size_callback(ctx, param, value: int) -> int:
    """
    Validates the disk size upon user input.

    Parameters
    ----------
    ctx
        Click context
    param
        Click parameter
    value: int

    Returns
    --------
    value: int
        Unmodified value if valid
    """
    if value < 100:
        raise click.BadParameter(DISK_SIZE_ERROR_MSG)

    return value

#!/usr/bin/env python3
# -*- coding:utf-8; mode:python -*-
#
# Copyright 2020, 2021 Pradyumna Paranjape
# This file is part of psprint.
#
# psprint is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# psprint is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with psprint.  If not, see <https://www.gnu.org/licenses/>.
#
"""
Read configuration files from default locations
"""

import configparser
import os
import sys
from pathlib import Path
from typing import Dict, List

import toml
import yaml

from .errors import BadMark
from .printer import PrintSpace


def _parse_yaml(config: Path, /) -> Dict[str, dict]:
    """
    Read configuration specified as a yaml file:
        - .psprintrc
        - style.yml
        - *.yml
    """
    with open(config, 'r') as rcfile:
        conf: Dict[str, dict] = yaml.safe_load(rcfile)
    if conf is None:  # pragma: no cover
        raise yaml.YAMLError
    return conf


def _parse_ini(config: Path, /, sub_section: bool = False) -> Dict[str, dict]:
    """
    Read configuration supplied in ``setup.cfg`` OR
        - *.cfg
        - *.conf
        - *.ini
    """
    parser = configparser.ConfigParser()
    parser.read(config)
    if sub_section:
        return {
            pspcfg.replace('psprint.', ''): dict(parser.items(pspcfg))
            for pspcfg in parser.sections() if 'psprint' in pspcfg
        }
    return {
        pspcfg: dict(parser.items(pspcfg))
        for pspcfg in parser.sections()
    }  # pragma: no cover


def _parse_toml(config: Path, /, sub_section: bool = False) -> Dict[str, dict]:
    """
    Read configuration supplied in ``pyproject.toml`` OR
        - *.toml
    """
    if sub_section:
        with open(config, 'r') as rcfile:
            conf: Dict[str, dict] = toml.load(rcfile).get('psprint', {})
        return conf
    with open(config, 'r') as rcfile:
        conf: Dict[str, dict] = dict(toml.load(rcfile))
    if conf is None:  # pragma: no cover
        raise toml.TomlDecodeError
    return conf


def _parse_rc(config: Path, /) -> Dict[str, dict]:
    """
    Parse psprintrc file

    Args:
        config: path to configuration file

    Returns:
        configuration sections

    Raises:
        BadMark: Bad configuration

    """
    if config.name == 'setup.cfg':
        # declared inside setup.cfg
        return _parse_ini(config, sub_section=True)
    if config.name == 'pyproject.toml':
        # declared inside pyproject.toml
        return _parse_toml(config, sub_section=True)
    try:
        # yaml configuration format
        return _parse_yaml(config)
    except yaml.YAMLError:
        try:
            # toml configuration format
            return _parse_toml(config)
        except toml.TomlDecodeError:
            try:
                # try generic config-parser
                return _parse_ini(config)
            except configparser.Error:
                raise BadMark(mark='configuration', config=str(config))


def read_config(custom: os.PathLike = None) -> PrintSpace:
    """
    Read psprint configurations from various locations

    Args:
        custom: custom location for configuration

    Returns:
        configured ``PrintSpace``

    Raises:
        BadMark- Bad configuration file format
    """

    # environment
    # assume POSIX
    user_home = Path(os.environ['HOME'])
    root_config = Path('/etc')
    xdg_config = Path(os.environ.get('XDG_CONFIG_HOME', user_home / '.config'))

    if sys.platform.startswith('win'):  # pragma: no cover
        # windows
        user_home = Path(os.environ['USERPROFILE'])
        root_config = Path(os.environ['APPDATA'])
        xdg_config = Path(
            os.environ.get('LOCALAPPDATA', user_home / 'AppData/Local'))

    # Preference of configurations *Most dominant first*
    config_heir: List[Path] = []

    # custom
    if custom is not None:
        if not Path(custom).is_file():
            raise FileNotFoundError(
                f'Custom configuration file: {custom} not found')
        config_heir.append(Path(custom))

    # environment variable
    psprintrc_var = os.environ.get('PSPRINTRC')
    if psprintrc_var is not None:
        if not Path(psprintrc_var).is_file():
            raise FileNotFoundError(
                f'PSPRINTRC configuration file: {psprintrc_var} not found')
        config_heir.append(Path(psprintrc_var))

    # current- and all parent- directories till project root or mountpoint
    # project root is the directory, which contains setup.(cfg|py) file
    current_dir = Path('.').resolve()
    while not (current_dir.is_mount()):
        if current_dir / '__init__.py':
            config_heir.append((current_dir / '.psprintrc'))
        if any((current_dir / setup).is_file()
               for setup in ('setup.cfg', 'setup.py')):
            config_heir.append((current_dir / 'pyproject.toml'))
            config_heir.append((current_dir / 'setup.cfg'))
            break
        current_dir = current_dir.parent

    # standard locations
    for heir in xdg_config, root_config, Path(__file__).parent.parent:
        for ext in '.yml', '.yaml', '.toml', '.conf':
            config_heir.append((heir / 'psprint/style').with_suffix(ext))

    # load configs from oldest ancestor to current directory
    default_print = PrintSpace()
    for config in reversed(config_heir):
        try:
            default_print.set_opts(_parse_rc(config), str(config))
        except (PermissionError, FileNotFoundError, IsADirectoryError):
            pass

    # initialize with config

    return default_print

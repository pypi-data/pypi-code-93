"""
Copyright (C) 2021 Athos Ribeiro

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
import configparser
import logging
import sys

__version__ = '0.2.0'

_defaults = {
    'log_level': 'warning',
    'log_file': 'stderr',
    'api_version': 'devel',
    'app_name': 'lppa',
    'lp_env': 'production'  # or staging
}

_log_level_map = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL
}

config = configparser.ConfigParser(defaults=_defaults)

_log_level_str = config['DEFAULT']['log_level']
_log_level = _log_level_map[_log_level_str]

_config_args = {'level': _log_level, 'format': '%(asctime)s %(levelname)s %(name)s: %(message)s'}

if config['DEFAULT']['log_file'] in ('stderr', 'stdout'):
    _config_args['stream'] = getattr(sys, config['DEFAULT']['log_file'])
else:
    _config_args['filename'] = config['DEFAULT']['log_file']

logging.basicConfig(**_config_args)

_logger = logging.getLogger(__name__)
_logger.debug(
    'Loaded PPA version %s with configurations %s from default values',
    __version__,
    dict(config['DEFAULT'])
)

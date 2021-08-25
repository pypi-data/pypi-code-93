# Microlib is a small collection of useful tools.
# Copyright 2020 Nicolas Hainaux <nh.techn@gmail.com>

# This file is part of Microlib.

# Microlib is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# any later version.

# Microlib is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Microlib; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import json
import shutil
from os import environ
from pathlib import Path

import toml

from .xdict import XDict


ALLOWED_FORMATS = {'json': json, 'toml': toml}


class StandardConfigFile():

    def __init__(self, appname, default_config_dir=None, filename=None,
                 firstrun_dialog=None, fileformat='json'):
        """
        Handle a user config file.

        The user config file will be located in the standard directory (e.g.
        '/home/username/.config/appname/' for Posix systems or
        'C:\\Users\\UserName\\AppData\\Roaming\\AppName\\' in Windows)
        and named after the appname and the chosen fileformat (e.g.
        appname.json or appname.toml).

        You can provide the path to a config file containing correct default
        values via default_config_dir parameter. If no default_config_dir is
        provided, then a default empty file will be used. Eitherwise, this
        default config file will be hereafter refered to as the default config
        file.

        Any attempt to load or save a nonexistent user config file (for
        instance, the first time, or if it has been removed), will lead to the
        default config file being copied as the new user config file. If you
        provided a firstrun_dialog function, then it is called and the user
        config file is updated with the values it returns.

        Once created, simply use .load() to get the settings as a dict and
        .save(data) to write updated data to the file (only the new or to be
        updated {key: values} pairs need to be provided to .save()).

        Available read-only property is path, what returns the full path to the
        user config file.

        :param appname: the name of your app
        :param default_config_dir: the directory where the default config file
                                   is to be found. Default config file's name
                                   must be the same as filename (and same
                                   extension too: either .toml or .json)
        :param filename: the filename to use. Defaults to appname.
        :param firstrun_dialog: a callable that is run if the user config file
                                does not exist. This callable must return a
                                dict.
        :param fileformat: only 'json' and 'toml' are supported. Defaults to
                           'json'.
        """
        self._fmt = ALLOWED_FORMATS[fileformat]
        if filename is None:
            filename = appname
        if firstrun_dialog is None:
            firstrun_dialog = self._default_firstrun_dialog
        if not callable(firstrun_dialog):
            raise TypeError('Argument \'firstrun_dialog\' must be a callable.')
        self._firstrun_dialog = firstrun_dialog
        if default_config_dir is None:
            self._default_config_file = \
                Path(__file__).parent \
                / f'data/empty_default_config.{fileformat}'
        else:
            self._default_config_file = \
                Path(default_config_dir) / f'{filename}.{fileformat}'
        configdir = environ.get('APPDATA') or environ.get('XDG_CONFIG_HOME')
        configdir = Path(configdir) if configdir else Path.home() / '.config'
        self._configdir = configdir / f'{appname}'
        self._user_config_file = self._configdir / f'{filename}.{fileformat}'

    @property
    def fullpath(self):
        """Full path to user config file (as Path object from pathlib)."""
        return self._user_config_file

    def _default_firstrun_dialog(self):
        return {}

    def _create_user_config_file(self):
        if not self._configdir.exists():
            self._configdir.mkdir(parents=True)
        shutil.copyfile(self._default_config_file, self._user_config_file)

    def _from(self, filename, ioerror_handling=None):
        data = XDict()
        try:
            with open(filename) as f:
                data = XDict(self._fmt.load(f))
        except FileNotFoundError:
            if ioerror_handling == 'firstrun_dialog':
                self._create_user_config_file()
                data = XDict(self._firstrun_dialog())
            else:
                raise
        return data

    def load(self):
        """Load the data of the config file."""
        data = self._from(self._default_config_file)
        data.recursive_update(
            self._from(self._user_config_file,
                       ioerror_handling='firstrun_dialog'))
        return data

    def save(self, new_data):
        """Update the config file with provided data."""
        data = self._from(self._user_config_file,
                          ioerror_handling='firstrun_dialog')
        data.recursive_update(new_data)
        with open(self._user_config_file, 'w') as config_file:
            self._fmt.dump(data, config_file)

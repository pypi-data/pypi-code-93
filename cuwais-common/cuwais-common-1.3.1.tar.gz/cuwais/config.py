import logging
from typing import Optional, Union

import yaml
import os


def _fill_in_defaults(data: Optional[Union[dict, list]], defaults: Optional[Union[dict, list]]):
    if data is None:
        return defaults

    if isinstance(data, list):
        return data

    if isinstance(data, dict):
        if not isinstance(defaults, dict):
            return data

        for key in data:
            data[key] = _fill_in_defaults(data[key], defaults.get(key, None))

        for key in defaults:
            if key not in data:
                data[key] = defaults[key]

        return data

    return data


class Config:
    def __init__(self, path: str, defaults: Optional[Union[dict, list, 'Config']] = None):
        if isinstance(defaults, Config):
            defaults = defaults.get_all()

        self._defaults = defaults

        if not os.path.isfile(path):
            logging.error(f"Could not find config file {path}")
            self._data = None
        else:
            with open(path, 'r') as stream:
                self._data = yaml.safe_load(stream)

        if self._defaults is None:
            self._defaults = dict()
        if self._data is None:
            self._data = dict()

        self._data = _fill_in_defaults(self._data, defaults)

    def get_all(self):
        return self._data

    def get(self, key: str):
        if not isinstance(key, str):
            raise RuntimeError("Key should be of type str")

        parts = key.split(".")

        data = self._data
        for part in parts:
            if data is None:
                break
            if isinstance(data, dict):
                data = data.get(part, None)
            elif isinstance(data, list):
                i = int(part)
                data = None if i >= len(data) or i < 0 else data[i]

        return data


default_config_file = Config("default_config.yml")
config_file = Config("config.yml", default_config_file)

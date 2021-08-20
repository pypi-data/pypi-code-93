import os
from pathlib import Path
from shutil import copyfile
from typing import Dict, Union

import yaml
from fontawesome import icons
from i3ipc.aio import Con
from xdg import XDG_CONFIG_HOME

POSSIBLE_SWAY_CONFIG_PATHS = ['sway', 'i3']

CONFIG_FILE_NAME = 'sdn-config.yaml'

DEFAULT_DELIMITER = "|"
DEFAULT_DEFAULT_ICON = "dot-circle"


class ConfigException(Exception):
    pass


class ClientConfig:
    def __init__(self, key: str, data: Union[str, Dict]):
        self.key = key
        if type(data) == str:
            self.icon = icons.get(data, data)
        elif type(data) == dict:
            self.icon = icons.get(data['icon'], data['icon'])
        else:
            raise ConfigException(f'clients/{key}: invalid entity {data}')

    def get_symbol(self, leaf: Con):
        return self.icon


class Config:
    _client_configs: Dict[str, ClientConfig] = {}
    _delimiter: str = "|"
    _last_modified: float = None

    def __init__(self, use_default=False):
        self.config_location = Config._find_config() if not use_default else Config._default_config_path()
        print(f"Using config file at {self.config_location}")

    def _load(self):
        if os.path.getmtime(self.config_location) != self._last_modified:
            with open(self.config_location, 'r') as f:
                data = yaml.safe_load(f)
            self._last_modified = os.path.getmtime(self.config_location)

            self._client_configs = {k: ClientConfig(k, v) for k, v in data.get('clients', {}).items()}
            self._delimiter = data.get('deliminator', DEFAULT_DELIMITER)
            self._default_icon = data.get('default_icon', DEFAULT_DEFAULT_ICON)
            self._default_icon = icons.get(self._default_icon, self._default_icon)

    @property
    def client_configs(self):
        self._load()
        return self._client_configs

    @property
    def delimiter(self):
        self._load()
        return self._delimiter

    @property
    def default_icon(self):
        self._load()
        return self._default_icon

    @staticmethod
    def _find_config():
        for possible_path in [pp.joinpath(CONFIG_FILE_NAME) for pp in Config._find_sway_folders()]:
            if possible_path.exists():
                return possible_path
        print(Config._find_sway_folders())
        return Config._create_config(Config._find_sway_folders()[0].joinpath(CONFIG_FILE_NAME))

    @staticmethod
    def _find_sway_folders():
        possible_paths = [XDG_CONFIG_HOME.joinpath(pp) for pp in POSSIBLE_SWAY_CONFIG_PATHS]
        return [pp for pp in possible_paths if pp.exists()]

    @staticmethod
    def _create_config(config_location: str):
        print(f"Creating default config file at {config_location}")
        copyfile(Config._default_config_path(), config_location)
        return config_location

    @staticmethod
    def _default_config_path():
        return Path(os.path.realpath(__file__)).parent.joinpath('default.yaml')

from pathlib import Path
from typing import Dict
from typing import Optional

import yaml

from quick.exception import ConfigException
from quick.exception import NotInitializedException


CURRENT_CONTEXT = "currentContext"
CONTEXTS = "contexts"
HOST = "host"
API_KEY = "apiKey"


class QuickConfig:
    def __init__(
        self,
        config_dir: str = ".config",
        config_file_name: str = "quick.conf",
        config_path: Path = None,
    ):
        self.config_path = config_path or self.__config_file_path(config_dir, config_file_name)
        self._config: Optional[Dict] = None

    @property
    def config(self) -> Dict:
        if self._config is None:
            self._config = self.__read_config()
        return self._config

    @config.setter
    def config(self, config: Dict):
        self._config = config

    # GET OPERATIONS

    def get_all(self):
        return self.config[CONTEXTS]

    def get_current_context(self) -> str:
        return self.config[CURRENT_CONTEXT]

    def get_host(self, context: str = None) -> str:
        return self.__get_value(HOST, context)

    def get_api_key(self, context: str = None) -> str:
        return self.__get_value(API_KEY, context)

    def get_current_context_config(self, context_name: str = None) -> Dict:
        try:
            context_name = context_name or self.get_current_context()
            return self.config[CONTEXTS][context_name]
        except KeyError:
            raise ConfigException(f"Context {context_name} not found")

    # UPDATE OPERATIONS

    def create(self, context: str, host: str, key: str):
        if self.__config_exists() and CONTEXTS in self.config:
            self.config[CONTEXTS][context] = {
                HOST: self.__prepare_host(host),
                API_KEY: key,
            }
        else:
            self.config = {
                CURRENT_CONTEXT: context,
                CONTEXTS: {context: {HOST: self.__prepare_host(host), API_KEY: key}},
            }
        self.__update_config()

    def set_host(self, host: str, context: str = None):
        self.__set_value(HOST, self.__prepare_host(host), context)

    def set_api_key(self, api_key: str, context: str = None):
        self.__set_value(API_KEY, api_key, context)

    def set_current_context(self, context: str):
        if self.config[CONTEXTS].get(context) is None:
            raise ConfigException(f"Context {context} does not exist. To create one, run: \n\t$ quick context create")
        self.config[CURRENT_CONTEXT] = context
        self.__update_config()

    # HELPER

    @staticmethod
    def __prepare_host(host) -> str:
        # Strip trailing '/' (required for correctly appending '/manager')
        if "/" in host[-1]:
            host = host[:-1]
        if not host.endswith("/manager"):
            # Append manager url
            host = host + "/manager"
        return host

    def __set_value(self, key: str, value: str, context: str = None):
        if context is None:
            context = self.config[CURRENT_CONTEXT]

        self.config[CONTEXTS][context][key] = value
        self.__update_config()

    def __get_value(self, key: str, context: str = None) -> str:
        if context is None:
            context = self.get_current_context()

        return self.config[CONTEXTS][context][key]

    def __update_config(self):
        with self.config_path.open("w", encoding="utf-8") as config_file:
            yaml.dump(self.config, config_file, default_flow_style=False)

    @staticmethod
    def __config_file_path(config_dir: str, config_file_name: str) -> Path:
        config_dir_path = Path.home().joinpath(config_dir)
        config_dir_path.mkdir(exist_ok=True)
        return config_dir_path.joinpath(config_file_name)

    def __config_exists(self):
        return self.config_path.exists() and self.config_path.stat().st_size > 0

    def __read_config(self) -> Dict:
        try:
            with self.config_path.open() as config_file:
                return yaml.safe_load(config_file)
        except FileNotFoundError:
            raise NotInitializedException

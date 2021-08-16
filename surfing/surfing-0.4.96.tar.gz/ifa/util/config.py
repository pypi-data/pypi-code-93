from . import Singleton
import platform
import json

CURRENT_PLATFORM = platform.system()
DEFAULT_CONFIG_PATH = '/shared/etc/ifa/config.json'

class Configurator(metaclass=Singleton):

    def __init__(self, config_path=DEFAULT_CONFIG_PATH):
        with open(config_path) as f:
            self.config = json.load(f)

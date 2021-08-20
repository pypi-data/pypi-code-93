"""
core class, for loading config.py and get parameters
"""

import os
import sys
import importlib

class PyConfig(object):
    def __init__(self, config):
        self.config_path = config
        if not os.path.exists(config):
            raise RuntimeError("config not exists")

        dir = os.path.dirname(config)
        base = os.path.basename(config)
        sys.path.append(dir)
        module_name = base.split(".")[0]

        self._cfg = importlib.import_module(module_name)

    def __getattr__(self, key):
        value = getattr(self._cfg, key, None)
        if value is None:
            raise RuntimeError("No config key: {} in {}".format(key, self.config_path))
        else:
            return value
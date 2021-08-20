from .py_config import PyConfig
from .yacs_config import yacsConfig
import os

def configParser(config: str):
    """
    create different config parser by file format
    :param config:
    :return:
    """
    assert os.path.exists(config), "not exists:{}".format(config)
    if config.endswith(".py"):
        return PyConfig(config)
    elif config.endswith((".yaml", ".yml")):
        return yacsConfig(config)
    else:
        raise RuntimeError("format of config is not supported")

import json
import os
from collections import OrderedDict

THEMES = OrderedDict({
    "Dark": "icon_dark.png",
    "Light": "icon_light.png",
})
APPLICATION_NAME = "python-pulseaudio-profiles-trayicon"


def config_dir():
    """
    Returns the config directory ($HOME/.config/python-pulseaudio-profiles-trayicon).

    :return: the directory for the configurations
    :rtype: str
    """

    return os.path.expanduser("~/.config/" + APPLICATION_NAME)


def config_file():
    """
    Returns the config file ($HOME/.config/python-pulseaudio-profiles-trayicon/config.json).

    :return: the directory for the configurations
    :rtype: str
    """

    return os.path.join(config_dir(), "config.json")


def init_config_dir():
    """
    Ensures that the config directory is present.

    :return: if directory present
    :rtype: bool
    """

    d = config_dir()
    if os.path.exists(d):
        return os.path.isdir(d)
    else:
        os.mkdir(d, mode=0o700)
        return True


def default_settings():
    """
    Returns the default settings.

    :return: the default settings
    :rtype: dict
    """
    return {
        "theme": "Dark",
    }


def load_config():
    """
    Loads the configuration from disk.

    :return: the configuration
    :rtype: dict
    """
    if not os.path.exists(config_dir()):
        init_config_dir()

    # load config from disk
    fname = config_file()
    if not os.path.exists(fname):
        result = dict()
    else:
        with open(fname, "r") as cf:
            result = json.load(cf)

    # fill in missing default values
    default = default_settings()
    for k in default:
        if k not in result:
            result[k] = default[k]

    return result
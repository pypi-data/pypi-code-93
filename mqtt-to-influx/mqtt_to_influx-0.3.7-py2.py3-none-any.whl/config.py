# pylint # {{{
# vim: tw=100 foldmethod=indent
# pylint: disable=bad-continuation, invalid-name, superfluous-parens
# pylint: disable=bad-whitespace, mixed-indentation
# pylint: disable=redefined-outer-name
# pylint: disable=missing-docstring, trailing-whitespace, trailing-newlines, too-few-public-methods
# }}}
import os
import logging
from pathlib import Path
from configparser import ConfigParser
from configparser import ExtendedInterpolation
from pathlib import Path
from mqtt_to_influx.parse_options import args

logger = logging.getLogger(__name__)

# CONFIG = ConfigParser()
CONFIG = ConfigParser(interpolation=ExtendedInterpolation())
CONFIG.optionxform = lambda option: option

def reload():
    """Reload configuration from disk.

    Config locations, by priority (all values are merged. The last one
        overwrites earlier ones)
    $MQTT_TO_INFLUX_CONFIG
    /etc/mqtt-to-influx/mqtt-to-influx.pathconf
    ./mqtt-to-influx.pathconf
    ~/.config/mqtt-to-influx/mqtt-to-influx.pathconf
    """
    files = []
    try:
        files += [ Path(args.pathconf_file) ]
    except:
        pass

    logger.info("reading pathconfig")

    filename = os.environ.get("MQTT_TO_INFLUX_CONFIG")
    if filename:
        files += [Path(filename)]

    files += [
        Path('/')/'etc'/'mqtt-to-influx'/'mqtt-to-influx.pathconf',
        Path.home()/'.config'/'mqtt-to-influx'/'mqtt-to-influx.pathconf',
        Path('./mqtt-to-influx.pathconf')
    ]

    logger.info("Using these config files: {} to find a suitable one".format(files))

    for f in files:
        if f.exists():
            logger.info("Using this config file: {}".format(f))
            CONFIG.read(f)
            break


# Load config on import
reload()

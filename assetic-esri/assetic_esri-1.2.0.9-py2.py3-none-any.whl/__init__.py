# coding: utf-8

"""
    Assetic ESRI Integration API

    OpenAPI spec version: v2
"""

from __future__ import absolute_import

import os
import sys

import logging

from assetic.tools import GISTools  # noqa
from assetic.tools.shared import CalculationTools  # noqa
from .__version__ import __version__  # noqa
from .config import Config  # noqa
from .initialise import Initialise  # noqa
from .settings.assetic_esri_config import LayerConfig  # noqa
from .tools.esri_layertools import LayerTools  # noqa
from .tools.legacy_layertools import LegacyLayerTools  # noqa
from .tools.legacy_commontools import CommonTools

# setup logging with some hardcoded settings so we can trap any initialisation
# errors which can be more difficult to trap when running in ArcGIS
logger = logging.getLogger(__name__)
appdata = os.environ.get("APPDATA")
logfile = os.path.abspath(appdata + r"\Assetic\addin.log")
if not os.path.isdir(os.path.abspath(appdata + r"\Assetic")):
    try:
        os.mkdir(os.path.abspath(appdata + r"\Assetic"))
    except Exception:
        # just put iti in appdata
        logfile = os.path.abspath(appdata + r"\addin.log")

f_handler = logging.FileHandler(logfile)
formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
f_handler.setFormatter(formatter)
logger.addHandler(f_handler)
logger.setLevel(logging.INFO)


def handle_uncaught_exception(exc_type, exc_value, exc_traceback):
    """
    If an exception is uncaught it isn't written to the log, so capture the
    exception here and write to the log.  It will also write to stderr
    :param exc_type: exception type
    :param exc_value: exception
    :param exc_traceback: traceback
    """
    sys.__excepthook__(exc_type, exc_value, exc_traceback)
    if not issubclass(exc_type, KeyboardInterrupt):
        logger.error(
            "Uncaught exception", exc_info=(exc_type, exc_value,
                                            exc_traceback))


sys.excepthook = handle_uncaught_exception

# don't remove this - initialises config singleton for python2
config = Config()

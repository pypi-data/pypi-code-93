from __future__ import absolute_import

from assetic.tools.shared import InitialiseBase
from . import Config
from .__version__ import __version__
from .tools.esri_messager import EsriMessager
import logging

class Initialise(InitialiseBase):
    def __init__(self, configfile=None, inifile=None, logfile=None, loglevelname=None):
        # initialise obejct here with all of the values we need
        conf = Config()
        conf.messager = EsriMessager()
        conf.xmlconfigfile = configfile
        conf.inifile = inifile
        conf.logfile = logfile
        conf.loglevelname = loglevelname

        super(Initialise, self).__init__(__version__, config=conf)
        # Get the assetic sdk file logger
        assetic_sdk_handle = None
        for sdk_handle in conf.asseticsdk.logger.handlers:
            if isinstance(sdk_handle, logging.handlers.RotatingFileHandler):
                assetic_sdk_handle = sdk_handle
                break

        # when the assetic-esri package is initiated a logger is created
        # to catch any issues that occur before this config instance is
        # initialised (%APPDATA%/addin.log)
        # Now we have a log file defined in the config we can remove
        # that handler and attach the sdk handler
        esri_logger = logging.getLogger(__name__).parent
        for handle in esri_logger.handlers:
            if type(handle) == logging.FileHandler:
                if assetic_sdk_handle:
                    esri_logger.removeHandler(handle)
                    # now attach the handler defined in the xml config file
                    esri_logger.addHandler(assetic_sdk_handle)
                    break
                elif conf.logfile:
                    # log file in XML but not initiating script so use that
                    # as the logger for assetic_esri logger
                    log_formatter = handle.formatter
                    esri_logger.removeHandler(handle)
                    new_handle = logging.FileHandler(conf.logfile)
                    new_handle.formatter = log_formatter
                    esri_logger.addHandler(new_handle)

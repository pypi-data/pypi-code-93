#!/usr/bin/env python

import logging
import logging.config
import os
import yaml
import sys
import argparse
from . import __version__
from typing import Optional, Union

DEFAULT_CONFIG    = os.getenv( 'CONFIGFILE', 'myapp.yaml' )
DEFAULT_LOGFILE   = os.getenv( 'LOGFILE', 'myapp.log' )

DEFAULT_LOGFORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DEFAULT_LOGLEVEL  = 'INFO'


def dictread( dictionary, key : str, default=None ):
    if dictionary is None:
        return default
    elif key in dictionary:
        return dictionary[key]
    else:
        return default


def forceread ( dictionary, key : str ):
    value = dictread(dictionary, key, None )
    if value is None:
        raise ValueError( f'Failed to read value {key} from configuration!')
    return value


def intreadNoneOk ( dictionary, key : str, default : Optional[int] = None ) -> Union[int, None]:
    if dictionary is None:
        return default
    else:
        val = dictread(dictionary, key, default)
        if val is not None:
            return int(val)
        else:
            return default


def intread ( dictionary, key : str, default : Optional[int] = None ) -> int:
    value = intreadNoneOk( dictionary, key, default )
    if value is not None:
        return value
    else:
        raise ValueError( f'Failed to read value {key} from configuration!')


class Config:

    c = None

    def __init__ ( self, filename=None ):

        if filename is None:
            filename = DEFAULT_CONFIG

        self.filename = filename
        self.readCommandLine()

        with open(self.filename) as source:
            self.config = yaml.load( source, Loader=yaml.FullLoader )

    def value ( self, key : str, default=None, fromBlock : str = None ):
        if not fromBlock:
            fromBlock = self.config
        return dictread(fromBlock, key, default)

    @staticmethod
    def get ( key : str, default=None, fromBlock : str = None ):
        return Config.c.value(key, default, fromBlock)

    def readCommandLine ( self ):

        parser = argparse.ArgumentParser(description='Generic UpDryTwist Command Parser')
        parser.add_argument('--config', help='Path to configuration file', default=None)
        args = parser.parse_args()
        if 'config' in vars(args):
            fileName = vars(args)['config']
            if fileName is not None:
                self.filename = fileName


def getConfig () -> Config :
    return Config.c


def loadConfig ():
    try:
        Config.c = Config()
    except Exception as e:
        print( "Cannot load configuration from file {}: {}".format( DEFAULT_CONFIG, str(e)))
        sys.exit(2)


class LoggingConfiguration:

    def __init__ ( self ):
        pass

    @staticmethod
    def initLogging ( config : Config, loggingBlock : str = 'Logging', baseConfigBlock : str = None ):
        loggingConfig = config.value( loggingBlock, None )
        incremental = dictread(loggingConfig, 'incremental', False )

        # Clean all handlers out of root . . . need this for testing when we reinitialize the handlers
        root = logging.getLogger()
        for h in list(root.handlers):
            root.removeHandler(h)

        if incremental or not loggingConfig:
            # if the configuration is incremental, or missing, we set up most of the logging
            # in particular, we need to manage formatter and handler

            logFile      = config.value( 'logfile',      DEFAULT_LOGFILE, baseConfigBlock )
            logFormat    = config.value( 'logformat',    DEFAULT_LOGFORMAT, baseConfigBlock )
            logLevel     = config.value( 'loglevel',     DEFAULT_LOGLEVEL, baseConfigBlock )
            logToConsole = config.value( 'logToConsole', False, baseConfigBlock )
            logToFile    = config.value( 'logToFile',    True, baseConfigBlock )

            root = logging.getLogger()
            root.setLevel( logLevel )

            if logToFile:
                handler = logging.FileHandler( logFile )
                # handler.setLevel( logLevel )
                handler.setFormatter( logging.Formatter(logFormat ))
                root.addHandler( handler )

            if logToConsole:
                handler = logging.StreamHandler( sys.stdout )
                # handler.setLevel( logLevel )
                handler.setFormatter( logging.Formatter(logFormat ))
                root.addHandler( handler )

        if loggingConfig:
            logging.config.dictConfig( loggingConfig )


def initialize ():
    loadConfig()
    LoggingConfiguration().initLogging( Config.c )
    logger = logging.getLogger(__name__)
    logger.info( f'Using updrytwist version {__version__} (from {__name__})')

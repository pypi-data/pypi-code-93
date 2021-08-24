#!/usr/bin/env python

# LIBS
from datetime import datetime
import traceback as trace

# LOGGING
import logging

# CREATE TOP LOG LEVEL
log = logging.getLogger("bravaorm")

# ADITIONAL LOG MANAGER
from .colored_log import ColoredFormatter
from .colors import *

def Logging(log_level='error'):
    
     if not len(log.handlers):

        _level = logging.ERROR
        if log_level == 'debug':
            _level = logging.DEBUG
        elif log_level == 'info':
            _level = logging.INFO
        elif log_level == 'warning':
            _level = logging.WARNING
        elif log_level == 'error':
            _level = logging.ERROR
        elif log_level == 'critical':
            _level = logging.CRITICAL

        _format = "%(levelname)s:\t  %(message)s"

        # Add console handler using our custom ColoredFormatter
        ch = logging.StreamHandler()
        ch.setLevel(_level)
        cf = ColoredFormatter(_format)
        ch.setFormatter(cf)
        log.addHandler(ch)

        # Set log level
        log.setLevel(_level)

def Info(message):
    log.info(message)

def Debug(message):
    log.debug(message)

def Warning(message):
    log.warning(message)

def Error(sector, e, traceback=True):
    _trace = None
    message = ""
    if traceback:
        _trace = trace.format_exc()
        message = f"\n {sector if sector else ''}: {_trace if _trace else ''} \n"
    log.error(f"{message} Message: {e if e else ''}")

def Critical(sector, e, traceback=True):
    _trace = None
    message = ""
    if traceback:
        _trace = trace.format_exc()
        message = f"\n {sector if sector else ''}: {_trace if _trace else ''} \n"
    log.critical(f"{message} Message: {e if e else ''}")

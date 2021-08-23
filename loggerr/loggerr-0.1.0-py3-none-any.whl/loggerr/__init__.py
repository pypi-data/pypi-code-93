# -*- coding: utf-8 -*-


from datetime import datetime
from json import dumps

levels = [
    'debug',
    'verbose',
    'info',
    'warn',
    'error',
    'critical'
]


class Loggerr:
    """ Create a JSON logger with minimal log level
    Args:
        logLevel (str): Minimal log level
    Example:
        logger = Loggerr('warn')
        logger.info('Something going as expected', { 'host': socket.gethostname() }) # ignored
        logger.error('Something must have gone terribly wrong') # sent
    """
    def __init__(self, logLevel='info'):
        minimum = levels.index(logLevel)
        for level in levels:
            if levels.index(level) < minimum:
                setattr(self, level, ignore)
            else:
                setattr(self, level, Log(level))


def ignore(message, enrichment={}):
    """ Ignore incoming log record
    Args:
        * match "log" function interface
    """
    return


def Log(level):
    """ Create a log function
    Args:
        level (str): The log level to attach
    Return:
        log (function)
    """
    def log(message, enrichment={}):
        """ Log JSON to stdout
        Args:
            message (str): String to log in records' "message" key
            enrichment (dic): More fields to appemnd to the log
        """
        record = {
            'message': message,
            'timestamp': str(datetime.now()),
            'level': level
        }
        print(dumps({**enrichment, **record}))
    return log

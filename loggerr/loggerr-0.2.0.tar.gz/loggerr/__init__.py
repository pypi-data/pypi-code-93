# -*- coding: utf-8 -*-

from traceback import format_exc
from datetime import datetime
from json import dumps

"""
Log levels in order of severity
"""
levels = [
    'debug',
    'verbose',
    'info',
    'warn',
    'error',
    'critical',
    'silent'
]

synonyms = [
    ['log', 'info'],
    ['warning', 'warn'],
    ['fatal', 'critical']
]


class Loggerr:
    """ Create a JSON logger with minimal log level
    Args:
        logLevel (str): Minimal log level (case insensitive)
    Example:
        logger = Loggerr('warn')
        logger.info('Something going as expected', { 'host': socket.gethostname() }) # ignored
        logger.error('Something must have gone terribly wrong') # sent
    """
    def __init__(self, logLevel='info'):
        minimum = levels.index(logLevel.lower())
        for level in levels:
            if levels.index(level) < minimum:
                setattr(self, level, ignore)
            else:
                setattr(self, level, Log(level))

        for synonym in synonyms:
            setattr(self, synonym[0], Log(synonym[1]))


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
            'timestamp': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
            'level': level
        }
        if (isinstance(message, Exception)):
            record['message'] = str(message)
            record['trace'] = format_exc(),
        else:
            record['message'] = message

        print(dumps({**enrichment, **record}))
    return log

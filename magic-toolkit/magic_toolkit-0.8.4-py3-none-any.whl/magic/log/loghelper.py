"""log helper"""

import logging
try:
    from termcolor import colored
    fmt = colored('[%(asctime)s]', 'blue') + \
          colored('%(levelname)s:', 'green') + \
          colored('%(message)s', 'white')
except Exception as err:
    fmt = '[%(asctime)s] %(levelname)s: %(message)s'

logging.basicConfig(level=logging.DEBUG, format=fmt, datefmt="%m-%d %H:%M:%S")

class LoggerWriter:
    _log_file_exists = False

    def __init__(self, filename='log.txt'):
        if LoggerWriter._log_file_exists:
            return
        fHandler = logging.FileHandler(filename, mode="w")
        fmt = '[%(asctime)s] %(levelname)s: %(message)s'
        formatter = logging.Formatter(fmt, datefmt="%y-%m-%d %H:%M:%S")
        fHandler.setLevel(logging.DEBUG)
        fHandler.setFormatter(formatter)
        logging.getLogger().addHandler(fHandler)
        LoggerWriter._log_file_exists = True

def to_string(*args):
    msglist = ["{}".format(x) for x in args]
    return ' '.join(msglist)

def debug(*args):
    logging.debug(to_string(*args))

def info(*args):
    logging.info(to_string(*args))

def warning(*args):
    logging.warning(to_string(*args))

def error(*args):
    logging.error(to_string(*args))

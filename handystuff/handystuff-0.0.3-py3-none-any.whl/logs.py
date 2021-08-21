import logging
import os
from logging.config import dictConfig
from logging.handlers import RotatingFileHandler

from handystuff.loaders import load_jsonnet
import tqdm


def setup_logging(path=None):
    """Setup logging configuration.

    Args:
      path:  (Default value = None)

    Returns:

    """
    from pkg_resources import resource_string
    path = path or resource_string(__name__, "resources/logging.conf")
    cfg = load_jsonnet(path)

    # noinspection PyUnresolvedReferences
    dictConfig(cfg)

    logging.getLogger(__name__).info("Config loaded.")


class MakeFileHandler(RotatingFileHandler):
    def __init__(self, filename, mode='a', maxBytes=0, backupCount=0,
                 encoding=None, delay=False):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        RotatingFileHandler.__init__(self, filename, mode, maxBytes,
                                     backupCount, encoding, delay)


class TQDMHandler(logging.StreamHandler):
    def __init__(self, *args, **kwargs):
        logging.StreamHandler.__init__(self, *args, **kwargs)

    def emit(self, record):
        msg = self.format(record)
        tqdm.tqdm.write(msg)


class FQNFilter(logging.Filter):
    def __init__(self, max_len=30):
        super().__init__()
        self.max_len = max_len

    def filter(self, record):
        fqn = ".".join((record.name, record.funcName))
        if len(fqn) > self.max_len:
            fqns = fqn.split(".")
            i = 0
            while sum(len(fqn) for fqn in fqns) + len(
                    fqns) - 1 > self.max_len and i < len(fqns):
                fqns[i] = fqns[i][0]
                i += 1
            fqn = ".".join(fqns)[:self.max_len]
        record.fqn = fqn
        return record


class Loggable:
    @property
    def logger(self):
        return logging.getLogger(
            ".".join((self.__module__, self.__class__.__name__)))

    @classmethod
    def get_class_logger(cls):
        return logging.getLogger(".".join((cls.__module__, cls.__name__)))

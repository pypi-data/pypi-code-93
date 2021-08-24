import inspect
import datetime
from pathlib import Path
from threading import RLock
import os
import sys
import traceback

try:
    from . import handlers
    from .constants import LoggerLevels
except ImportError:
    import handlers
    from constants import LoggerLevels


class Logger:
    _instance = None
    _log_path = None
    _instantiated_by = None
    _lock = RLock()

    def __new__(cls, path=None):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instantiated_by = inspect.stack()[0].function

            cls._log_path = cls._resolve_log_path(path)

            cls._handlers = []

            cls.add_handler(handlers.RotatingFileHandler(cls._log_path, backup_count=100))
            cls.add_handler(handlers.StreamHandler(sys.stdout))

        return cls._instance

    @classmethod
    def add_handler(cls, handler):
        cls._lock.acquire()
        try:
            if handler not in cls._handlers:
                cls._handlers.append(handler)
        finally:
            cls._lock.release()

    @classmethod
    def remove_handler(cls, handler):
        cls._lock.acquire()
        try:
            if handler in cls._handlers:
                cls._handlers.remove(handler)
        finally:
            cls._lock.release()

    @classmethod
    def _resolve_log_path(cls, path):
        if path is None:
            root_path = Path(cls._get_caller_directory())

            log_dir = root_path / '.logs'

            if not log_dir.is_dir():
                os.mkdir(log_dir)

            path = log_dir / (cls._get_time_string("%y_%m_%d__%H_%M_%S" + '.log'))

        else:
            if isinstance(path, Path):
                path = path / (cls._get_time_string("%y_%m_%d__%H_%M_%S" + '.log'))
            else:
                path = Path(path) / (cls._get_time_string("%y_%m_%d__%H_%M_%S" + '.log'))

        return path

    def _log(self, msg, *, level, raise_exc=False, exc_info=False):

        msg = self._get_time_string("%d/%m/%y %H:%M:%S") + \
            f'[{inspect.stack()[2].function}]' + \
            f'[{os.path.abspath(inspect.stack()[2].filename)}:{inspect.stack()[2].lineno}]' + \
            f'[{LoggerLevels().level_to_str(level)}] ' + msg

        for handler in self._handlers:
            handler.handle(msg, level)
            if exc_info:
                handler.handle(traceback.format_exc(), level)

        if raise_exc:
            sys.exit(1)

    def format(self, *args, **kwargs):

        sep = kwargs.pop('sep', ' ')
        prefix = kwargs.pop('prefix', '')
        end = kwargs.pop('end', '')

        if end.startswith('\n'):
            end = end[1:]
        elif end.endswith('\n'):
            end = end[:-1]

        return prefix + sep.join(map(str, args)) + end

    def info(self, *args, **kwargs):

        msg = self.format(*args, **kwargs)

        self._log(msg, level=LoggerLevels.info)

    def warning(self, *args, **kwargs):

        msg = self.format(*args, **kwargs)

        self._log(msg, level=LoggerLevels.warning)

    def error(self, *args, **kwargs):
        exc_info = kwargs.pop('exc_info', None)

        msg = self.format(*args, **kwargs)

        self._log(msg, level=LoggerLevels.error, exc_info=exc_info)

    def exception(self, *args, **kwargs):
        msg = self.format(*args, **kwargs)

        self._log(msg, level=LoggerLevels.error, raise_exc=True, exc_info=True)

    @staticmethod
    def _get_caller_directory():
        return Path(inspect.stack()[3].filename).parent

    @staticmethod
    def _get_time_string(fmt: str = ''):
        return datetime.datetime.now().strftime(fmt)


if __name__ == '__main__':

    logger = Logger()

    text = input()

    logger.info(text)
    logger.warning(text)
    logger.error(text)
    try:
        0/0
    except Exception:
        logger.exception()

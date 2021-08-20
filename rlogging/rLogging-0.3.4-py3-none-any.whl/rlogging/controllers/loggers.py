""" Модуль учета логгеров """
import multiprocessing as _M
import typing as _T

from rlogging import config, utils
from rlogging.entities.base import BaseLogger
from rlogging.entities.loggers import Logger


class LoggersController(object):
    """ Интерфейс управления логерами """

    __loggers: dict[str, BaseLogger]

    logStorageQueue: _M.Queue

    def __init__(self) -> None:
        self.__loggers = {}

    def set(self, logStorageQueue: _M.Queue):
        self.logStorageQueue = logStorageQueue

    def check(self, loggerName: str) -> bool:
        return loggerName in self.__loggers

    def create(self, loggerName: str, loggerClass: _T.Optional[type[BaseLogger]] = None):
        if loggerName in self.__loggers:
            raise ValueError('Логгер "{0}" уже существует'.format(
                loggerName
            ))

        if loggerClass is None:
            loggerClass = utils.get_obj(config.RLOGGING_LOGGER)

        self.__loggers[loggerName] = loggerClass(loggerName)
        self.__loggers[loggerName].set(self.logStorageQueue)

    def get(self, loggerName: str) -> Logger:
        if not self.check(loggerName):
            self.create(loggerName)

        return self.__loggers[loggerName]

    def apply_settings(self, loggingSettings: dict):
        """ Настройка логгеров и создание не существующих

        Args:
            loggingSettings (dict): Настройки логеров

        """

        for loggerName, loggerInfo in loggingSettings['loggers'].items():
            if not self.check(loggerName):
                self.create(
                    loggerName,
                    utils.get_obj(loggerInfo['logger_class'])
                )

            targetLogger = self.get(loggerName)
            targetLogger.load_data(loggerInfo['settings'])

""" Модуль кастомизируемого логирования """

from rlogging import entities
from rlogging.controllers import loggersController
from rlogging.setup.controller import rloggingSetup

# alpha release
__version__ = '0.3.4'


def get_logger(loggerName: str) -> entities.loggers.Logger:
    """ Получение логера по имени

    Args:
        loggerName (str): Имя логера

    Returns:
        Logger: Логгер

    """

    return loggersController.get(loggerName)

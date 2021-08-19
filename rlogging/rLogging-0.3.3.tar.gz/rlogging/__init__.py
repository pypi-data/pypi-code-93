""" Модуль кастомизируемого логирования """

from rlogging.setup.controller import rloggingSetup
from rlogging import entities
from rlogging.controllers import loggersController
# alpha release
__version__ = '0.3.3'


def get_logger(loggerName: str) -> entities.loggers.Logger:
    """ Получение логера по имени

    Args:
        loggerName (str): Имя логера

    Returns:
        Logger: Логгер

    """

    return loggersController.get(loggerName)

""" Информационные исключения """

import typing as _T
from dataclasses import dataclass

import rlogging
from rcore import exception as ex

logger = rlogging.get_logger('mainLogger')


class rExInfo(ex.exception.rEx):
    """ Информационное исключение """

    text: _T.Union[str, None] = None

    def __init__(self, description: _T.Union[str, None], text: _T.Union[str, None] = None):
        if description is not None:
            self.description = description

        if text is not None:
            self.text = text

    def print(self):
        logger.exception(self)
        print(self.text)


class DDExit(rExInfo):
    """ Вспомогательное исключение для завершения выполнения кода при вызове utils.dd """

    description = 'DD - method for detailed code debugging'


@dataclass
class CliHelpPrint(rExInfo):
    """ Вывод информации от CLI. """

    text: str


@dataclass
class CliErrorRequired(rExInfo):
    """ Пропуск обязательного аргумента у команды. """

    text: str


@dataclass
class CliErrorType(rExInfo):
    """ Указано недопустимое типом значение для параметра. """

    text: str

""" Исключения - ошибки """

from __future__ import annotations

import typing as _T
from dataclasses import dataclass

import rlogging
from rcore import exception as ex

logger = rlogging.get_logger('mainLogger')


class rExError(ex.exception.rEx):
    """ Исключение подразумевающее ошибку выполнения """

    def print(self):
        logger.exception(self)

        if self.traceback:
            print('Traceback:')
            self.traceback.print()
            print()

        if self.description is not None:
            print(type(self).__name__ + ': ' + self.description)


class rException(rExError):
    """ Обертка над встроенными исключениями python """

    def __init__(self, exLevel: Exception):
        self.description = type(exLevel).__name__ + ': ' + str(exLevel)


class DeveloperIsShitError(rExError):
    """ Вспомогательное исключение для ловли ситуаций, которые, казалось бы, я предусмотрел """

    def __init__(self, message: str = 'ну тупой'):
        self.description = message


class NotInitPathError(rExError):
    """ Задействован модуль rpath без инициализации RootPaths """

    description = 'Корневые пути проекта не были инициализированны.'


class DirNotFile(rExError):
    """ Попытка выполнить файловую операцию к директори """

    def __init__(self, path):
        self.description = f'You tried to apply a file operation to a folder: "{0}"'.format(
            path
        )


class FileNotDir(rExError):
    """ Попытка выполнить папочную операцию к файлу """

    def __init__(self, path):
        self.description = f'You tried to perform a folder operation on a file: "{0}"'.format(
            path
        )


class NotInitConfig(rExError):
    """ Не инициализирована конфигурация """

    description = 'Not init config data'


class NotInitConfigFile(rExError):
    """ Не обьявлен именованный файл конфигурации """

    def __init__(self, file):
        self.description = "Config file named {0} not initialized".format(
            file
        )


class CliErrorParseArgument(rExError):
    """ В команде содержится невалидный аргумент """

    def __init__(self, word: str):
        self.description = 'В команде содержится невалидный аргумент: "{}"'.format(
            word
        )


@dataclass
class CliArgumentError(rExError):
    """ Ошибка в обработчике команды запуска """

    description: str


class ItemNotFound(rExError):
    """ В неком наборе значений не найден искомый элемент """

    def __init__(self, array: _T.Any, key: str):
        if isinstance(array, dict):
            self.description = 'in an array where keys are: {0} en will find the key "{1}"'.format(
                list(array.keys()), key
            )
        else:
            self.description = 'In list "{0}" key "{1}" not found.'.format(
                array, key
            )


class NoChangeType(rExError):
    """ Невозможно привести к типу """

    def __init__(self, expected: type, received: _T.Any):
        self.description = 'Cannot cast value "{0}" to type "{1}"'.format(
            received, received
        )
        
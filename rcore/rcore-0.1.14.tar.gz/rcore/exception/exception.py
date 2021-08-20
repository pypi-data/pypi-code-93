from __future__ import annotations

import functools
import sys
import typing as _T
from copy import copy

import rcore
import rlogging
from rcore import exception as ex

logger = rlogging.get_logger('mainLogger')


def print_python_traceback():
    """ Вывести в консоль python исключение """

    if rcore.main.__debug_mod__:
        ex.traceback.print_traceback()
        print()


class rEx(BaseException):
    """ Extended Exception Class

    Values:
        description (str): exception description

    """

    description: _T.Union[str, None] = None

    traceback: _T.Union[ex.traceback.BaseTracebackStage, None] = None

    def __str__(self):
        if self.description is None:
            return 'Extended Exception Class'
        return self.description

    def __init__(self, description: _T.Union[str, None] = None):
        if description is not None:
            self.description = description

    def append_traceback(self, tb: ex.traceback.BaseTracebackStage):
        logger.info('Добавление к исключению "{0}" стадию пользовательского трейсбека "{1}"'.format(
            self.__class__.__name__,
            tb.__class__.__name__
        ))

        child = copy(self.traceback)
        self.traceback = tb
        if child:
            self.traceback.add_child(child)
        return self

    def print(self):
        """ Вывод исключения в консоль """

        logger.exception(self)

        print(type(self).__name__ + ': ', sep='', end='')
        if self.description:
            print(self.description, end='')

        print()

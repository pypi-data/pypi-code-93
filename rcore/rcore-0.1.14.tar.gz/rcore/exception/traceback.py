""" Пользовательские трейсбеки """

from __future__ import annotations

import sys
import traceback
import typing as _T

import rlogging
from rcore import utils

logger = rlogging.get_logger('mainLogger')


def print_traceback(pyEx: _T.Optional[BaseException] = None):
    """ Вывод python трейсбека в консоль """

    if pyEx is None:
        exc_type, exc_value, exc_tb = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_tb)
    
    else:
        traceback.print_exception(
            type(pyEx),
            pyEx,
            pyEx.__traceback__
        )


def save_traceback():
    """ Сохранение python трейсбека в cache """

    fileName = '/tmp/r.l'

    with open(fileName, 'w') as f:
        exc_type, exc_value, exc_tb = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_tb, file=f)


class BaseTracebackStage(object):
    """ Класс пользовательского трейсбека.

    Используется внутри приложения для демонстрации проблемы пользователя.

    """

    child: _T.Optional[BaseTracebackStage]

    def __init__(self):
        self.child = None

    def add_child(self, tp: BaseTracebackStage):
        searchchelid = self
        while True:
            if not searchchelid.child:
                break
            searchchelid = searchchelid.child
        searchchelid.child = tp

    def print(self):
        """ Вывод сообщений всего дерева пользовательских трейсбеков """

        logger.info('Вывод пользовательского трейсбека')

        messages = self.messages()

        logger.debug('Трейсбек состоит из следующих сообщений: "{0}"'.format(
            messages
        ))

        print()
        print('Traceback of custom actions:')
        for messageLvl in messages:
            if messageLvl[2] is None:
                print(' ' * 2, 'Сообщение одной из стадии трейсбека')
                print(' ' * 4, messageLvl[1], sep='')

            else:
                print(' ' * 2, messageLvl[1], sep='')
                print(' ' * 4, messageLvl[2], sep='')

    def messages(self) -> list[tuple[str, str]]:
        """ Формирование сообщений всего дерева пользовательских трейсбеков.

        Returns:
            list[tuple[str, str]]: Сообщения

        """

        logger.debug('Формировани списка сообщений дерева пользовательских трейсбеков. Стадия "{0}"'.format(
            self.__class__.__name__
        ))

        messages = []

        messages.append(self.message())

        if self.child:
            messages += self.child.messages()

        return messages

    def message(self) -> tuple[_T.Type[BaseTracebackStage], _T.Optional[str], _T.Optional[str]]:
        return (
            self,
            'Базовый класс пользовательского трейсбека',
            None
        )


class TextTracebackStage(BaseTracebackStage):
    """ Стадия трейсбека состоящая из некоторого текста """

    firstLineText: str
    secondLineText: _T.Optional[str]

    def __init__(self, firstLineText: str, secondLineText: _T.Optional[str] = None):
        super().__init__()

        self.firstLineText = firstLineText
        self.secondLineText = secondLineText

    def message(self) -> tuple[_T.Type[BaseTracebackStage], _T.Optional[str], _T.Optional[str]]:
        return (
            self,
            self.firstLineText,
            self.secondLineText
        )


class ConfigTracebackStage(BaseTracebackStage):
    """ Трейсбек ссылающийся на значения в неком словаре (конфигурации приложения) """

    dictpath: list[str]
    errorValue: str
    secondLineText: str

    def __init__(self, dictpath: list[str], errorValue: _T.Any, secondLineText: str):
        super().__init__()

        self.dictpath = dictpath
        self.errorValue = str(errorValue)
        self.secondLineText = secondLineText

    def message(self) -> tuple[_T.Type[BaseTracebackStage], _T.Optional[str], _T.Optional[str]]:
        return (
            self,
            'Config: {0}, error value: {1}'.format(
                ' > '.join(self.dictpath),
                self.errorValue
            ),
            self.secondLineText
        )


_spanFile = _T.Union[
    tuple[int, int],
    list[tuple[int, int]],
    None
]


class FileTracebackStage(BaseTracebackStage):
    """ Трейсбек ссылающийся файл и некоторый диапазон символов в нем """

    fileName: str
    spanFile: _spanFile

    def __init__(self, fileName: str, spanFile: _spanFile = None):
        super().__init__()

        self.fileName = fileName
        self.spanFile = spanFile

    def message(self):
        filePath = utils.rPath(self.fileName)

        if self.spanFile is not None:
            spans = self.spanFile if isinstance(self.spanFile, list) else [self.spanFile]

            start_line = utils.search_point_by_lines(filePath, spans[0][0])
            spans_text = utils.file_span_separate(filePath, spans)

            return (
                self,
                'File "{0}", line {1}'.format(
                    filePath,
                    str(start_line)
                ),
                ' ... '.join(spans_text)
            )

        return (
            self,
            'File "{0}"'.format(
                filePath
            ),
            'Error in this file'
        )

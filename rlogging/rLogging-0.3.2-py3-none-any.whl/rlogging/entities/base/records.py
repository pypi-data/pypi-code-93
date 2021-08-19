import inspect
import os
import threading
import time
import typing as _T
from itertools import chain
import multiprocessing as _M
from rlogging import config, utils


class BaseRecord(object):
    """ Базовый лог """

    __slots__ = (
        'loggerName', 'logLevel', 'message', 'kwargs',

        'timestamp', 'pidId', 'processName', 'threadId',
        'fromModule', 'fromFile', 'fromFileLine', 'fromObject',

        'loggingLevelLabel', 'loggingLevelLabelCenter',
        'time',
    )

    # Поля из вне
    loggerName: str
    logLevel: int
    message: str
    kwargs: dict[str, str]

    # Поле определившиеся при инициализации
    timestamp: float
    pidId: int
    processName: str
    threadId: int
    #
    fromModule: str
    fromFile: str
    fromFileLine: str
    fromObject: str

    # Поля которые появятся после форматирования
    loggingLevelLabel: str
    loggingLevelLabelCenter: str

    time: str

    @classmethod
    @property
    def __all_slots__(cls) -> _T.Iterable:
        """ Получение списка всех доступных параметров, основнном на переменной __slot__

        Returns:
            _T.Iterable: Список доступных параметров

        """

        return chain.from_iterable(getattr(subClass, '__slots__', []) for subClass in cls.__mro__)

    def __init__(self, loggerName: str, logLevel: int, message: str, kwargs: dict[str, str]) -> None:
        self.loggerName = loggerName
        self.logLevel = logLevel
        self.message = message
        self.kwargs = kwargs

        self._gen_fields()

    def _gen_fields(self):
        self.timestamp = time.time()
        self.pidId = os.getpid()
        self.processName = _M.current_process().name
        self.threadId = threading.get_ident()

        # на 5 уровня вверх от данной функции (определяется эксперементальным путем)
        stack = inspect.stack()[6]
        module = inspect.getmodule(stack.frame)

        self.fromModule = module.__name__
        self.fromFile = stack.filename
        self.fromFileLine = stack.lineno

        self.fromObject = stack.function

        # Если у функции есть атрибут self / cls значит она метод класса.
        if 'self' in stack.frame.f_locals:
            self.fromObject = '{0}.{1}'.format(
                stack.frame.f_locals.get('self').__class__.__name__,
                stack.function
            )

        elif 'cls' in stack.frame.f_locals:
            self.fromObject = '{0}.{1}'.format(
                stack.frame.f_locals.get('cls').__name__,
                stack.function
            )

    @classmethod
    def create_record(cls, loggerName: str, logLevel: int, message: str, kwargs: dict[str, str]):
        return cls(loggerName, logLevel, message, kwargs)

    @staticmethod
    def create_default_record(loggerName: str, logLevel: int, message: str, kwargs: dict[str, str]):
        recordClass: BaseRecord = utils.get_obj(config.RLOGGING_RECORD)
        return recordClass.create_record(loggerName, logLevel, message, kwargs)

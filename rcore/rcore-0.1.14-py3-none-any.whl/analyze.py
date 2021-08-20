""" Модуль аналитики приложения.

Через добавление декораторов позволяет анализировать использование функций.

Работает в тандеме с unit-тестированием или любым другим способом задействовать функции.

Чтобы пропустить анализ некого объекта.
    У него должен быть под-объект __analyze__ равный False

"""

from __future__ import annotations

import functools
import time
import types
import typing as _T
from datetime import datetime

import rlogging

from rcore import utils
from rcore.rpath import rPath

logger = rlogging.get_logger('mainLogger')

__analyze__ = False

ANALYZE_OUTPUT_FILE = 'lorem.xlsx'


class Counter(object):
    """ Объект для сбора аналитики """

    functions: list = []
    count: list = []
    time: list[list[float]] = []

    def add_function(self, functionName: str):
        """ Добавление в статистику функции """

        self.functions.append(functionName)
        self.count.append(0)
        self.time.append([])

    def save(self, analyticsFolderPath: rPath):
        """ Сохранение собранной аналитики в файл """

        import pandas as pd

        timeColum: list[_T.Union[int, float]] = []

        for values in self.time:

            if len(values) == 0:
                timeColum.append(0)
                continue

            time_ = float(0)
            for value in values:
                time_ += value

            # item = timedelta(milliseconds=time_ / len(values)).microseconds * 100000000
            item = time_ * 1000

            timeColum.append(item)

        df = pd.DataFrame({
            'Name': self.functions,
            'Count': self.count,
            'Time': timeColum
        })

        if not analyticsFolderPath.check():
            analyticsFolderPath.create()

        analyticsFile = analyticsFolderPath.merge(
            f'{datetime.timestamp(datetime.now())}.analytics.xlsx'
        )

        df.to_excel(str(analyticsFile))


def obj_name(obj: types.FunctionType, parantObj: object):

    parentName = None
    if isinstance(parantObj, type):
        parentName = parantObj.__name__

    if parentName:
        return '.'.join([
            obj.__module__, parentName, obj.__name__
        ])

    return '.'.join([
        obj.__module__, obj.__name__
    ])


class Analyze(object):
    """ Класс осуществляющий анализ выполнения кода в функциях """

    objHistory: list[int]
    counter: Counter

    def __init__(self):
        self.objHistory = []
        self.counter = Counter()

    def analyze(self, func: types.FunctionType, obj: object, args: tuple[_T.Any], kwargs: dict[str, _T.Any], result: _T.Any, leadTime: tuple[float, float]):

        funcName = obj_name(func, obj)

        counterIndex = self.counter.functions.index(funcName)

        self.counter.count[counterIndex] += 1
        self.counter.time[counterIndex].append(
            leadTime[1] - leadTime[0]
        )

    def decorator(self, func: types.FunctionType, obj: object):
        """ Декоратор, для анализируемых функций """

        funcName = obj_name(func, obj)

        logger.debug(f'Добавление декоратора на функцию "{funcName}"')

        self.counter.add_function(funcName)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):

            start_time = time.monotonic()
            result = func(*args, **kwargs)
            end_time = time.monotonic()

            self.analyze(func, obj, args, kwargs, result, (start_time, end_time))

            return result

        return wrapper

    def init(self, moduleName: str):
        module = __import__(moduleName, None, None, ['suite'])
        self.parse(module, [moduleName])

    def parse(self, obj: object, assesModules: list[str]):
        """ Поиск подходящих для анализа объектов.

        Если у объект есть параметр __analyze__ равный False, то объект пропускается.

        """

        if id(obj) in self.objHistory:
            return

        self.objHistory.append(id(obj))

        logger.debug(f'Анализ модуля {obj}')

        objDir = dir(obj)

        if '__analyze__' in objDir and not getattr(obj, '__analyze__'):
            return

        for objKey in objDir:
            objParam = getattr(obj, objKey)

            #  Модули
            if isinstance(objParam, types.ModuleType):
                if objParam.__name__.split('.')[0] in assesModules:
                    self.parse(objParam, assesModules)

            # Функции и методы
            elif isinstance(objParam, types.FunctionType):
                if objParam.__module__.split('.')[0] in assesModules:
                    setattr(obj, objKey, self.decorator(objParam, obj))

            # Классы
            elif isinstance(objParam, type):
                if objParam.__module__.split('.')[0] in assesModules:
                    self.parse(objParam, assesModules)

            else:
                pass

    def save(self, analyticsFolderPath: rPath):
        """ Сохранить результаты измерений """

        self.counter.save(analyticsFolderPath)


analyzeProcessing = Analyze()


@utils.debugmod(anywaySkip=True)
def init(moduleName: str):
    """ Инициализация аналитики """

    return None
    logger.info('Инициализация модуля аналитики приложения')

    analyzeProcessing.init(moduleName)


@utils.debugmod(anywaySkip=True)
def stop():
    """  Остановка аналитики """

    return None
    logger.info('Остановка модуля аналитики приложения')

    analyzeProcessing.save(rPath('analytics', fromPath='cache'))

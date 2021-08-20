""" Модуль для обозначения точки входа в программу

Этот функционал нужен для:
* Корректной ловли и обработки исключений
* Профайлинга

"""

import cProfile
import functools
import pstats
import time
import typing as _T

import rlogging

from rcore import exception as ex
from rcore.rpath import rPath

logger = rlogging.get_logger('mainLogger')


def exception_handler(exception: BaseException):
    """ Обработка исключений, которые произошли в декораторе d_entrypoint

    Args:
        exception (BaseException): [description]

    """

    if isinstance(exception, ex.rEx):
        ex.exception.print_python_traceback()
        exception.print()

    elif isinstance(exception, BaseException):
        logger.exception(exception)
        ex.exception.print_python_traceback()


def call_target_fun(targetFunc: _T.Callable, args: tuple, kwargs: dict, stopCallback: _T.Callable) -> _T.Any:
    """ Вызов функции точки входа

    Args:
        targetFunc (_T.Callable): Функция - точка входа
        args (tuple): Параметры
        kwargs (dict): Параметры
        stopCallback (_T.Callable): Функция корректной остановки приложения

    Returns:
        _T.Any: Результат функции targetFunc

    """

    result = None

    try:
        result = targetFunc(*args, **kwargs)

    except BaseException as exception:
        logger.warning('Программа завершилась из-за исключения')
        exception_handler(exception)

    else:
        logger.info('Программа завершилась без исключений')

    finally:
        stopCallback()

    return result


def profile_handler(profile: cProfile.Profile):
    """ Обработка профалейра выполнения функции - точки входа

    Args:
        profile (cProfile.Profile): Профайлер "with cProfile.Profile() as profile:"

    """

    stats = pstats.Stats(profile)
    stats.sort_stats(pstats.SortKey.TIME)

    for fileKeyname in ('last', round(time.time())):
        filename = 'profiles/{0}.prof'.format(
            fileKeyname
        )

        filePath = rPath(filename, fromPath='cache')
        filePath.create()
        stats.dump_stats(str(filePath))


def d_entrypoint(stopCallback: _T.Union[_T.Callable, None] = None) -> _T.Callable:
    """ Декоратор для функции точки входа

    Args:
        stopCallback (_T.Union[_T.Callable, None], optional): Функция, которая обеспечивает корректную остановку приложения. Defaults to None.

    Returns:
        _T.Callable: Функция wrapper декоратора

    """

    def wrapper(targetFunc: _T.Callable):

        @functools.wraps(targetFunc)
        def inner(*args, **kwargs):
            with cProfile.Profile() as profile:
                result = call_target_fun(targetFunc, args, kwargs, stopCallback)
                profile_handler(profile)

            return result

        return inner
    return wrapper

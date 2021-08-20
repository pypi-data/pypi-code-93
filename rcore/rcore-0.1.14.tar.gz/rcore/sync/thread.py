""" Модуль для асинхронного выполнения неких действий в отдельных потоках """

import multiprocessing as _M
import threading as _Th
import typing as _T


class OnThreadMixin(object):
    """ Миксин для выполнения кода некого класса в отдельном потоке """

    @classmethod
    def run_thread(cls, *args, **kwargs) -> _Th.Thread:
        """ Создание потока с таргетом на функцию on_thread этого класса

        Args:
            args (_T.Any): Значения для инициализации объекта.
            kwargs (_T.Any): Значения для инициализации объекта.

        Returns:
            _Th.Thread: Новый процесс

        """

        logger.debug('Создание потока для выполнения кода класса "{0}"'.format(
            cls.__name__
        ))

        threadObj = cls(*args, **kwargs)

        return _Th.Thread(target=threadObj.on_thread)

    def on_thread(self):
        """ Эта функция будет запускаться в отдельном потоке

        Raises:
            ValueError: Класс не переопределил функцию "on_thread"

        """

        raise ValueError('Класс "{0}" не переопределил функцию "on_thread"'.format(
            self.__class__.__name__
        ))

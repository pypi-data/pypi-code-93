""" Модуль для асинхронного выполнения неких действий в отдельных процессах """


import multiprocessing as _M
import sys
import traceback
import typing as _T
from multiprocessing import pool as _MP
import rlogging
from rcore.exception.traceback import print_traceback

logger = rlogging.get_logger('mainLogger')


class ExceptionWrapper(object):
    """ Обертка для исключений для проноса их сквозь процессы """

    exception: BaseException

    def __init__(self, exception):
        self.exception = exception

    def re_raise(self):
        raise self.exception


class OnProcessMixin(object):
    """ Миксинг для запуска некого класса в отдельном потоке """

    @classmethod
    def run_process(cls, *args, **kwargs) -> _M.Process:
        """ Создание процесса с таргетом на функцию on_process этого класса

        Args:
            args (_T.Any): Значения для инициализации объекта.
            kwargs (_T.Any): Значения для инициализации объекта.

        Returns:
            _M.Process: Новый процесс

        """

        logger.debug('Создание процесса для выполнения кода класса "{0}"'.format(
            cls.__name__
        ))

        return _M.Process(target=cls.on_process_entrypoint, args=args, kwargs=kwargs)

    @classmethod
    def on_process_entrypoint(cls, *args, **kwargs) -> _T.Union[_T.Any, ExceptionWrapper]:
        """ Функция с которой начинается запуск процесса.

        Этот метод вызовет метод on_process.

        Args:
            args (_T.Any): Значения для инициализации объекта.
            kwargs (_T.Any): Значения для инициализации объекта.

        Returns:
            _T.Optional[BaseException]: Исключение произошедшее в процессе
            _T.Any: Результат выполнения функции

        """

        try:
            return cls(*args, **kwargs).on_process()

        except BaseException as ex:
            return ExceptionWrapper(ex)

    def on_process(self):
        """ Эта функция будет запускаться в отдельном процессе

        Raises:
            ValueError: Класс не переопределил функцию "on_process"

        """

        raise ValueError('Класс "{0}" не переопределил функцию "on_process"'.format(
            self.__class__.__name__
        ))


class NoDaemonProcess(_M.Process):
    """ Класс процесса, который нельзя будет сделать демоническим """

    def _get_daemon(self):
        return False

    def _set_daemon(self, value):
        pass

    daemon = property(_get_daemon, _set_daemon)


class NoDaemonPool(_MP.Pool):
    """ Класс пула процессов, который не будут демоническими """

    @staticmethod
    def Process(ctx, *args, **kwds):
        return NoDaemonProcess(*args, **kwds)


class BaseProcessesPoolController(object):
    """ Пул для запуска обработки некого класса в отдельных процессах """

    Pool: type[_MP.Pool] = _MP.Pool

    poolParams: list[tuple[tuple, dict]]
    results: list[_T.Any]
    targetClass: OnProcessMixin

    def __init__(self, targetClass: OnProcessMixin) -> None:
        self.poolParams = []
        self.results = []
        self.targetClass = targetClass

    def add_process(self, *args, **kwargs):
        """ Добавление в пул параметров для нового процесса

        Args:
            args (_T.Any): Значения для инициализации объекта.
            kwargs (_T.Any): Значения для инициализации объекта.

        """

        self.poolParams.append(
            (args, kwargs)
        )

    def map(self):
        """ Запуск """

        args = [i[0] for i in self.poolParams]

        with self.Pool(len(args)) as pool:
            results = pool.starmap(self.targetClass.on_process_entrypoint, args)

        for result in results:
            if isinstance(result, ExceptionWrapper):
                result.re_raise()

            self.results.append(result)


class ProcessesPoolController(BaseProcessesPoolController):
    """ Пул для запуска обработки некого класса в отдельных процессах """

    Pool = _MP.Pool


class NoDeamonProcessesPoolController(BaseProcessesPoolController):
    """ Пул для запуска обработки некого класса в отдельных не демонических процессах.

    Нужен дял того, чтобы запускать несколько пулов друг в друге

    """

    Pool = NoDaemonPool

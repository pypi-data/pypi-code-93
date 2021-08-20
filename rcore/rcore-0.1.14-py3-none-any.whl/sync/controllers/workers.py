import multiprocessing as _M
import typing as _T
from rcore.sync.controllers import managers

import rlogging

logger = rlogging.get_logger('mainLogger')


class BaseControllerWorker(object):
    """ Базовый worker класс, который осуществляет контроллерскую работы """

    manager: managers.BaseControllerManager

    def target(self, manager: managers.BaseControllerManager):
        self.manager = manager

        logger.info('Воркер контроллера "{0}". Стадия: Запуск выполнения'.format(
            self.__class__.__name__,
        ))

        self.worker()

    def worker(self):
        """ Функция, которая будет запускаться в новом процессе """

    def exception_handler(self, processKey: str, exception: BaseException):
        """ Обработка исключения пришедшего из обрабатываемого процесса

        Args:
            processKey (str): Идентификатор процесса
            exception (BaseException): исключения обрабатываемого процесса

        """

        logger.warning('От обрабатываемого процесса "{0}" пришло исключение "{1}"'.format(
            processKey,
            exception
        ))

        raise exception

    def get_data(self) -> dict[str, _T.Any]:
        """ Получение данных из очередей

        Returns:
            dict[str, _T.Any]: Словарь процессов и их данных

        """

        logger.info('Контроллер Воркер "{0}". Получение данных из обслуживаемых процессах'.format(
            self.__class__.__name__,
        ))

        inputtedData: dict[str, _T.Any] = {}

        for processKey, queue in self.manager.inputtedQueue.items():
            inputtedData[processKey] = queue.get()

            if isinstance(inputtedData[processKey], BaseException):
                self.exception_handler(processKey, inputtedData[processKey])
                break

        return inputtedData

    def put_data(self, outputtedData: dict[str, _T.Any]):
        """ Выдача результатов обработки

        Args:
            outputtedData (dict[str, _T.Any]): Данные для выдачи

        """

        for processKey, processOutputQueue in self.manager.outputtedQueue.items():
            processOutputQueue.put(outputtedData[processKey])

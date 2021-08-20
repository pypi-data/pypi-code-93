import multiprocessing as _M
from types import TracebackType

import rlogging
from rcore.sync.controllers import managers, workers

logger = rlogging.get_logger('mainLogger')


class BaseController(object):
    """ Базовый класс интерфейса для обмена сообщениями между контроллером и процессами """

    workerClass: type[workers.BaseControllerWorker] = workers.BaseControllerWorker
    worker: workers.BaseControllerWorker

    managerClass: type[managers.BaseControllerManager] = managers.BaseControllerManager
    manager: managers.BaseControllerManager

    process: _M.Process

    def __init__(self, *args, **kwargs):
        """ Инициализация контроллера.

        Переданные параметры будут переданы в инициализацию workerClass.

        Args:
            args (tuple): Параметры инициализации workerClass.
            kwargs (dict): Параметры инициализации workerClass.

        """

        self.manager = self.managerClass()
        self.worker = self.workerClass(*args, **kwargs)

    def start_worker(self):
        """ Запуск worker процесса """

        logger.info('Контроллер "{0}". Стадия: Запуск воркера. Воркер будет обслужить {1}*2={2} очередей'.format(
            self.__class__.__name__,
            len(self.manager.inputtedQueue),
            len(self.manager.inputtedQueue) * 2
        ))

        self.process = _M.Process(target=self.worker.target, args=(self.manager, ))
        self.process.start()

    def stop_worker(self):
        """ Остановка worker процесса """

        self.process.join()
        self.process.terminate()

    def __enter__(self):
        logger.info('Контроллер "{0}". Стадия: Создание менеджера контекста'.format(
            self.__class__.__name__,
        ))

        self.start_worker()

        return self.manager

    def __exit__(self, exceptionClass: type[BaseException], exception: BaseException, exceptionTraceback: TracebackType):
        if exceptionClass is not None:
            logger.error('В контексте менеджера котроллера "{0}" произошло исключение: {1}'.format(
                self.__class__.__name__,
                exception
            ))
            raise exception.with_traceback(exceptionTraceback)

        logger.debug('Завершение работы менеджера контекста контроллера "{0}"'.format(
            self.__class__.__name__
        ))

        self.stop_worker()

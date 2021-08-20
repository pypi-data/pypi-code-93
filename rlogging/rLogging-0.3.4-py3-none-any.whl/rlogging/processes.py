import multiprocessing as _M
import traceback
from multiprocessing.connection import Connection
from multiprocessing.managers import ValueProxy
from time import sleep

from rlogging import config


class SubProcessWorker(object):
    """ Воркер, обрабатывающий логи в своем процессе """

    logQueue: _M.Queue
    onWhile: ValueProxy[bool]
    setupWorkerPipe: Connection

    def set(self, logQueue: _M.Queue, onWhile: ValueProxy[bool], setupWorkerPipe: Connection):
        self.logQueue = logQueue
        self.onWhile = onWhile
        self.setupWorkerPipe = setupWorkerPipe

    def apply_settings(self, settings: dict):
        raise ValueError('И что с этим дедать')

    def processing(self):
        raise ValueError('И что с этим дедать')

    def __empty_logs_queue(self):
        """ Итерация по объектам логов, пока не очистится очередь """

        while not self.logQueue.empty():
            self.processing()

    def _get_settings(self):

        if not self.setupWorkerPipe.poll(0):
            return

        settings = self.setupWorkerPipe.recv()

        self.__empty_logs_queue()

        try:
            self.apply_settings(settings)

        except BaseException as ex:
            print('Трейсбек внутри воркера "{0}" при применении настроек логоирования:'.format(
                self.__class__.__name__
            ))
            print(traceback.format_exc())
            self.setupWorkerPipe.send(ex)
            return

        self.setupWorkerPipe.send(True)

    def _handle_logs_and_settings(self):
        while self.onWhile.value:
            self._get_settings()
            self.__empty_logs_queue()
            sleep(0.1)

        self.__empty_logs_queue()

        if self.logQueue.qsize() > 0:
            raise ValueError('fuck')

    def on_process(self):
        self._handle_logs_and_settings()


class SubProcessController(object):
    """ Хендлер, обрабатывающий логи в дополнительном процессе """

    logQueue: _M.Queue
    onWhile: ValueProxy[bool]
    setupControllerPipe: Connection

    worker_class: type[SubProcessWorker] = SubProcessWorker
    worker: SubProcessWorker

    process: _M.Process

    def __init__(self):
        self.worker = self.worker_class()

    def set(self, logQueue: _M.Queue, onWhile: ValueProxy[bool], setupPipe: tuple[Connection, Connection]):
        """ Установка необходимых переменных, для синхронизации состояния между процессами

        Args:
            logQueue (_M.Queue): Очередь с логами
            onWhile (ValueProxy[bool]): Должен ли быть этот процесс активным
            setupPipe (tuple[Connection, Connection]): Pipe для обновления настроек

        """

        self.logQueue = logQueue
        self.onWhile = onWhile
        self.setupControllerPipe = setupPipe[0]

        self.worker.set(logQueue, onWhile, setupPipe[1])

    def start(self):
        """ Запуск процесса контроллера """

        self.process = _M.Process(target=self.worker.on_process)
        self.process.start()

    def stop(self):
        """ Запуск процесса контроллера """

        self.onWhile.value = False

    def apply_settings(self, loggingSettings: dict):
        """ Отправка в хендлер новых настроек логирования.

        Выполнение блокируется, пока настройки не вступят в силу.

        Args:
            loggingSettings (dict): Настройки логирования

        Raises:
            ValueError: При применении настроек воркер вернул исключение

        """

        self.setupControllerPipe.send(loggingSettings)

        if not self.setupControllerPipe.poll(config.RLOGGING_WAIT_APPLY_SETTINGS):
            raise ValueError(
                'Истекло время применения настроек воркером "{0}". '
                'Попробуйте увеличить параметр "RLOGGING_WAIT_APPLY_SETTINGS"'.format(
                    self.worker_class.__name__
                )
            )

        response = self.setupControllerPipe.recv()

        if response is True:
            return

        if isinstance(response, BaseException):
            raise ValueError('При применении настроек воркер "{0}" вернул исключение: {1}'.format(
                self.worker_class.__name__,
                repr(response)
            ))

        raise ValueError('При применении настроек воркер "{0}" вернул невалидное значение: {1}'.format(
            self.worker_class.__name__,
            response
        ))

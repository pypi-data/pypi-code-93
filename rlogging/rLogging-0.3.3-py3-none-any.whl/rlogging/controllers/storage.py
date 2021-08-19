""" Контроллер сбора и распределения логов """

import multiprocessing as _M
import typing as _T
from queue import Queue
from time import sleep

from rlogging import processes, utils
from rlogging.entities.base import (BaseHandler, BaseLogger, BasePrinter,
                                    BaseRecord)

MAX_ARCHIVE_SIZE = 500


class StorageEntitiesWorkerMixin(object):

    loggers: dict[str, BaseLogger]
    handlers: dict[str, list[BaseHandler]]

    def _create_entities(self, loggingSettings: dict):
        """ Создание объектов логирования, объявленных в настройках

        Args:
            loggingSettings (dict): Настройки логирования

        """

        for loggerName, loggerInfo in loggingSettings['loggers'].items():
            loggerClass = utils.get_obj(loggerInfo['logger_class'])
            self.loggers[loggerName] = loggerClass.cls_load_data(
                loggerInfo['settings']
            )

        for _, handlerInfo in loggingSettings['handlers'].items():
            handlerClass = utils.get_obj(handlerInfo['handler_class'])
            newHandler = handlerClass.cls_load_data(
                handlerInfo['settings']
            )

            parentLoggerName = handlerInfo.get('parentLoggerName')

            if parentLoggerName not in self.handlers:
                self.handlers[parentLoggerName] = []

            self.handlers[parentLoggerName].append(
                newHandler
            )

    def _start_entities(self, loggingSettings: dict):
        """ Запуск хендлеров и передача настроек

        Args:
            loggingSettings (dict): Настройки логирования

        """

        for _, handlersPool in self.handlers.items():
            for handler in handlersPool:
                handler.start()
                handler.apply_settings(loggingSettings)

    def _stop_entities(self):
        for _, handlersPool in self.handlers.items():
            for handler in handlersPool:
                handler.stop()

        self.loggers = {}
        self.handlers = {}


class StorageControllerWorker(processes.SubProcessWorker, StorageEntitiesWorkerMixin):
    """ Воркер контроллер передачи логов из логгеров в хендлеры """

    archiveQueue: Queue
    archiveStatus: bool

    def __init__(self):
        self.archiveQueue = Queue(MAX_ARCHIVE_SIZE)
        self.archiveStatus = True

        self.loggers = {}
        self.handlers = {}

    def apply_settings(self, loggingSettings: dict):
        self._stop_entities()
        self._create_entities(loggingSettings)
        self._start_entities(loggingSettings)

        self.archiveStatus = False

    def processing_record(self, record: BaseRecord):
        """ Обработка пришедший в хранилище логов.

        Алгоритм:
        * получение лога
        * проверка, нужно ли обрабатывать этот лог (по имени логгера и настройкам)
        * передача лога всем хендлерам

        Args:
            record (BaseRecord): Обрабатываемый лог

        """

        if record.loggerName not in self.loggers:
            errorMessage = 'Лог "{0}" был сделан логером "{1}", который не был настроен. Лог пропускается.'.format(
                record.message,
                record.loggerName
            )

            if 'mainLogger' in self.loggers:
                mainLogger = self.loggers.get('mainLogger')
                mainLogger.error(errorMessage)

            else:
                print(errorMessage)

            return

        parentLogger = self.loggers[record.loggerName]

        if not parentLogger.need_processing(record):
            return

        for handler in self.handlers[record.loggerName]:
            handler.transfer(record)

    def processing(self):

        if self.archiveStatus:
            # Статус логера "archiveStatus=True"
            # Все пришедшие логи уходят в локальный архив,
            # до изменения статуса на "archiveStatus=False"
            self.archiveQueue.put(
                self.logQueue.get()
            )

        elif not self.archiveQueue.empty():
            # Статус логера "archiveStatus=False",
            # но еще не все логи из архива были обработаны
            # Передача логов их архива в обработчик
            self.processing_record(
                self.archiveQueue.get()
            )

        else:
            # Передача логов от логгеров в обработчик
            self.processing_record(
                self.logQueue.get()
            )

    def on_process(self):
        self._handle_logs_and_settings()
        self._stop_entities()


class StorageController(processes.SubProcessController):
    """ Контроллер передачи логов из логгеров в хендлеры """

    worker_class = StorageControllerWorker

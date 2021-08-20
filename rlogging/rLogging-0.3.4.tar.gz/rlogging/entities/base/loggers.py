
from __future__ import annotations

import multiprocessing as _M
import typing as _T

from rlogging.entities.base import BaseRecord
from rlogging.entities.base.main import BaseLoggingEntity


class CoreLogger(BaseLoggingEntity):
    """ Ядро логера """

    __setup_fields__ = (
        'name', 'minLogLevel'
    )

    name: str
    minLogLevel: int = 0

    logsStorageQueue: _M.Queue

    def __init__(self, name: str):
        self.name = name

    def need_processing(self, record: BaseRecord) -> bool:
        """ Проверка необходимости обрабатывать лог.

        Может получиться так, что после применения настроек уровень логирования поднимется
        И уже отправленные в хранилище логи станут неактуальными.

        Так же тут может быть специфичные условия пользователей.

        Args:
            record (BaseRecord): Объект лога

        Returns:
            bool: Нужно ли обрабатывать лог

        """

        if self.name != record.loggerName:
            return False

        elif self.minLogLevel > record.logLevel:
            return False

        return True

    def set(self, logsStorageQueue: _M.Queue):
        self.logsStorageQueue = logsStorageQueue

    def transfer(self, record: BaseRecord):
        """ Передача лога в хендлеры.

        Если логер не запущен, лог попадет в архив.

        Args:
            record (BaseRecord): Объект лога

        """

        if not self.need_processing(record):
            return

        self.logsStorageQueue.put(record)


class BaseLogger(CoreLogger):
    """ Базовый логер """

    def _log(self, logLevel, message: str, kwargs: dict[str, str]) -> BaseRecord:
        """ Создать объекта лога и передача его в хранилище.

        Args:
            logLevel (int): Уровень лога
            message (str): Сообщение лога
            kwargs (dict): Доп параметры

        Returns:
            BaseRecord: Объект лога

        """

        if self.minLogLevel > logLevel:
            return

        record = BaseRecord.create_default_record(self.name, logLevel, message, kwargs)

        self.transfer(record)

        return record

    def log(self, logLevel, message: str, **kwargs: dict[str, str]):
        """ Создать лог уровня logLevel.

        Args:
            logLevel (int): Уровень лога
            message (str): Сообщение лога
            kwargs (dict): Доп параметры

        """

        self._log(logLevel, message, kwargs)


class DevNullLogger(BaseLogger):
    """ Логгер для создания логов без отправки их в хранилище """

    def transfer(self, record: BaseRecord):
        pass

    def log(self, logLevel, message: str, **kwargs: dict[str, str]) -> BaseRecord:
        return self._log(logLevel, message, kwargs)

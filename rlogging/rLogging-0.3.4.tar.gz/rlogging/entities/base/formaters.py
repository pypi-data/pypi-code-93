
import re
import types
import typing as _T
from datetime import datetime

import rlogging
from rlogging.entities.base import BaseRecord
from rlogging.entities.base.main import BaseLoggingEntity


class BaseFormater(BaseLoggingEntity):
    """ Базовый форматер """

    def formate(self, record: BaseRecord) -> str:
        """ Создание строки из данных лога

        Raises:
            AttributeError: Дочерний класс не переназначил данный метод

        """

        raise AttributeError('Форматер "{0}" не переназначил функцию форматирования'.format(
            self.__class__.__name__
        ))

    def start_clean_functions(self, record: BaseRecord):
        """ Вызов функций начинающихся с `add_` и `clean_`

        Args:
            record (BaseRecord): Объект лога

        """

        methodsNames = dir(self)

        addingMethods = []
        cleaningMethods = []

        for methodName in methodsNames:
            method = getattr(self, methodName)

            if isinstance(method, types.MethodType):
                if method.__name__.startswith('add_'):
                    addingMethods.append(method)

                elif method.__name__.startswith('clean_'):
                    cleaningMethods.append(method)

        for method in addingMethods:
            method(record)

        for method in cleaningMethods:
            method(record)

    def record_to_dict(self, record: BaseRecord, allowKeys: _T.Optional[_T.Iterable[str]] = None) -> dict:
        if allowKeys is None:
            allowKeys = record.__all_slots__

        recordDict = {
            field: getattr(record, field) if hasattr(record, field) else None for field in allowKeys
        }

        if 'kwargs' in recordDict and isinstance(recordDict['kwargs'], dict):
            del recordDict['kwargs']

        recordDict.update(record.kwargs)

        return recordDict

    def processing(self, record: BaseRecord) -> str:
        self.start_clean_functions(record)
        return self.formate(record)


class BaseFormaterMixin(object):
    """ Миксин для добавления основных полей """

    timeFormat: str = '%H:%M:%S.%f'

    def add_time(self, record: BaseRecord):
        """ Перевод timestamp в привычное время

        Args:
            record (BaseRecord): Объект лога

        """

        time_on_datetime = datetime.fromtimestamp(record.timestamp)
        record.time = time_on_datetime.strftime(self.timeFormat)

    def add_logging_level_label(self, record: BaseRecord):
        """ Добавление лейбла уровня лога

        Args:
            record (BaseRecord): Объект лога

        """

        for maxSroreForLevel, loggingLevelLabel in rlogging.levels.LOGGING_LEVELS.items():
            if maxSroreForLevel >= record.logLevel:
                record.loggingLevelLabel = loggingLevelLabel
                record.loggingLevelLabelCenter = loggingLevelLabel.center(8)
                break

    def add_message(self, record: BaseRecord):
        """ Удаление всех лишних символов из сообщения лога

        Args:
            record (BaseRecord): Объект лога
        """

        record.message = re.sub(r'[\s]+', ' ', record.message)

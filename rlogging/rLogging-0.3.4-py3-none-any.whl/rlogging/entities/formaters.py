import json
import re
import typing as _T

from rlogging.entities.base import BaseFormater
from rlogging.entities.base.formaters import BaseFormaterMixin
from rlogging.entities.base import BaseRecord
from rlogging.setup.proxy import LoggingSetupEntityProxy


class LineFormater(BaseFormater, BaseFormaterMixin):
    """ Форматер, создающий на основе лога строку по указанному формату """

    __setup_fields__ = ('timeFormat', 'messageFormat')

    messageFormat: str = """
        %(time)s - %(pidId)s:%(threadId)s -
        %(loggingLevelLabelCenter)s - %(loggerName)s -
        %(fromModule)s:%(fromFileLine)s %(fromObject)s -
        %(message)s
    """

    @classmethod
    def setup(cls, **kwargs) -> LoggingSetupEntityProxy:
        """ Создание прокси для настройки форматера

        Args:
            kwargs: Значение полей настроки. Подробнее в Kwargs

        Kwargs:
            messageFormat (str): Формат лога, в котором он будет принтиться
            timeFormat (str): Формат даты, в котором она будет принтиться

        Returns:
            LoggingSetupEntityProxy: Прокси настроки форматера LineFormater

        """

        entityProxy = super().setup('formater', **kwargs)
        entityProxy.settings['messageFormat'] = re.sub(r'[\s]+', ' ', entityProxy.settings['messageFormat'])

        return entityProxy

    def formate(self, record: BaseRecord) -> str:
        recordDict = self.record_to_dict(record)

        try:
            return self.messageFormat % recordDict

        except KeyError as ex:
            return 'Не получилось отформатировать лог "{0}", так как для реализации шаблона "{1}" не было нужной переменной: {2}'.format(
                record.message,
                self.messageFormat,
                ex.args[0]
            )


class StructureFormater(BaseFormater, BaseFormaterMixin):
    """ Форматер, создающий на основе лога json строку с указанными полями """

    __setup_fields__ = ('timeFormat', 'allowKeys')

    allowKeys: _T.Optional[_T.Iterable[str]] = None

    @classmethod
    def setup(cls, **kwargs) -> LoggingSetupEntityProxy:
        """ Создание прокси для настройки форматера

        Args:
            kwargs: Значение полей настроки. Подробнее в Kwargs

        Kwargs:
            allowKeys (str): Параметры лога, которые будут в конечном json словаре
            messageFormat (str): Формат даты, в котором она будет принтиться

        Returns:
            LoggingSetupEntityProxy: Прокси настроки форматера StructureFormater

        """

        return super().setup('formater', **kwargs)

    def formate(self, record: BaseRecord) -> str:
        recordDict = self.record_to_dict(record, self.allowKeys)
        return json.dumps(recordDict)

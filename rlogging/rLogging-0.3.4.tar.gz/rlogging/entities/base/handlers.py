from rlogging import utils
from rlogging.entities.base import BaseFormater, BasePrinter, BaseRecord
from rlogging.entities.base.main import BaseLoggingEntity
from rlogging.setup.proxy import LoggingSetupEntityProxy


class CoreHandler(BaseLoggingEntity):
    """ Еще более базовый хендлер """

    __setup_fields__ = ('name', 'minLogLevel')

    name: str
    minLogLevel: int = 0

    printers: dict[str, BasePrinter]
    formaters: dict[str, BaseFormater]

    def __init__(self, name: str):
        self.name = name

        self.printers = {}
        self.formaters = {}

    @classmethod
    def setup(cls, **kwargs) -> LoggingSetupEntityProxy:
        """ Создание прокси для настройки хендлера

        Args:
            kwargs: Значение полей настроки. Подробнее в Kwargs

        Kwargs:
            name (str): Имя хендлера
            minLogLevel (str): Минимальный уровень лога, который будет обрабатываться хендлером

        Returns:
            LoggingSetupEntityProxy: Прокси настроки логгера Logger

        """

        return super().setup('handler', **kwargs)


class BaseHandler(CoreHandler):
    """ Базовый хендлер """

    def apply_settings(self, loggingSettings: dict):
        """ Обновление настроек логирования

        Args:
            loggingSettings (dict): Настройки логирования

        """

        for printerName, printerInfo in loggingSettings['printers'].items():
            if printerInfo['parentHandlerName'] != self.name:
                continue

            printerClass = utils.get_obj(printerInfo['printer_class'])
            self.printers[printerName] = printerClass.cls_load_data(
                printerInfo['settings']
            )

        for _, formaterInfo in loggingSettings['formaters'].items():
            if formaterInfo['parentPrinterName'] not in self.printers:
                continue

            formaterClass = utils.get_obj(formaterInfo['formater_class'])
            self.formaters[formaterInfo['parentPrinterName']] = formaterClass.cls_load_data(
                formaterInfo['settings']
            )

    def transfer(self, record: BaseRecord):
        """ Передача лога в очередь обработки

        Args:
            record (BaseRecord): Объект лога

        """

        if self.minLogLevel > record.logLevel:
            return

        for printerName, printer in self.printers.items():
            formater = self.formaters[printerName]

            recordString = formater.processing(record)
            printer.processing(record, recordString)

    def start(self):
        pass

    def stop(self):
        pass

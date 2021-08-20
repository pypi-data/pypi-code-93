import copy
from pprint import pprint

from rlogging import utils
from rlogging.controllers import loggersController, storageController
from rlogging.entities.base import (BaseFormater, BaseHandler, BaseLogger,
                                    BasePrinter)
from rlogging.setup.proxy import LoggingSetupEntityProxy

"""
# Пример результата построения дерева
_tree = {
    'loggers': {
        'loggerName': {
            'logger_class': '',
            'setting': {
                # настройки хендлера (dump_data)
            }
        }
    },
    'handlers': {
        'handlerName': {
            'parentLoggerName': '',
            'handler_class': '',
            'setting': {
                # настройки хендлера (dump_data)
            }
        }
    },
    'printers': {
        'printerName': {
            'parentHandlerName': '',
            'printer_class': '',
            'setting': {
                # настройки хендлера (dump_data)
            }
        }
    },
    'formaters': {
        'formaterName': {
            'parentPrinterName': '',
            'formater_class': '',
            'setting': {
                # настройки принтера (dump_data)
            }
        }
    }
}
"""


class BaseSetupTree(object):
    """ Основа интерфейс для настройки логирования """

    _tree: dict

    def __init__(self) -> None:
        self.filling_tree()

    def filling_tree(self):
        self._tree = {}

        for entity in ('loggers', 'handlers', 'printers', 'formaters'):
            self._tree[entity] = {}

    def dump_settings(self) -> dict:
        """ Получение настроек логирование в виде словаря

        Returns:
            dict: Настройки логирование

        """

        return copy.deepcopy(self._tree)


class ValidationSetupTree(BaseSetupTree):
    """ Интерфейс для валидации настроек """

    def __validation_loggers(self):
        for loggerName, loggerInfo in self._tree['loggers'].items():
            try:
                utils.get_obj(loggerInfo['logger_class'])

            except (ImportError, AttributeError) as ex:
                raise ValueError('Логгер "{0}" не прошел валидацию. Не получилось импортировать класс "{1}". Ошибка: {2}'.format(
                    loggerName, loggerInfo['logger_class'], ex
                ))

    def __validation_handlers(self):
        for handlerName, handlerInfo in self._tree['handlers'].items():
            try:
                utils.get_obj(handlerInfo['handler_class'])

            except (ImportError, AttributeError) as ex:
                raise ValueError('Хендлер "{0}" не прошел валидацию. Не получилось импортировать класс "{1}". Ошибка: {2}'.format(
                    handlerName, handlerInfo['handler_class'], ex
                ))

    def __validation_printers(self):
        for printerName, printerInfo in self._tree['printers'].items():
            try:
                utils.get_obj(printerInfo['printer_class'])

            except (ImportError, AttributeError) as ex:
                raise ValueError('Принтер "{0}" не прошел валидацию. Не получилось импортировать класс "{1}". Ошибка: {2}'.format(
                    printerName, printerInfo['printer_class'], ex
                ))

    def __validation_formaters(self):
        for formaterName, formaterInfo in self._tree['formaters'].items():
            try:
                utils.get_obj(formaterInfo['formater_class'])

            except (ImportError, AttributeError) as ex:
                raise ValueError('Форматер "{0}" не прошел валидацию. Не получилось импортировать класс "{1}". Ошибка: {2}'.format(
                    formaterName, formaterInfo['formater_class'], ex
                ))

    def validation(self):
        self.__validation_loggers()
        self.__validation_handlers()
        self.__validation_printers()
        self.__validation_formaters()


class SetSetupTree(BaseSetupTree):
    """ Надстройка на BaseSetupTree реализующая интерфейс установки сущностей логирования """

    def set_logger(self, loggerProxy: LoggingSetupEntityProxy):
        if loggerProxy.name in self._tree['loggers']:
            return

        self._tree['loggers'][loggerProxy.name] = {
            'logger_class': loggerProxy.classPath,
            'settings': loggerProxy.dump_settings()['settings']
        }

    def set_handler(self, loggerProxy: LoggingSetupEntityProxy, handlerProxy: LoggingSetupEntityProxy):
        if handlerProxy.name in self._tree['handlers']:
            return

        self._tree['handlers'][handlerProxy.name] = {
            'parentLoggerName': loggerProxy.name,

            'handler_class': handlerProxy.classPath,
            'settings': handlerProxy.dump_settings()['settings']
        }

    def set_printer(self, handlerProxy: LoggingSetupEntityProxy, printerProxy: LoggingSetupEntityProxy):
        if printerProxy.name in self._tree['printers']:
            return

        self._tree['printers'][printerProxy.name] = {
            'parentHandlerName': handlerProxy.name,

            'printer_class': printerProxy.classPath,
            'settings': printerProxy.dump_settings()['settings']
        }

    def set_formater(self, printerProxy: LoggingSetupEntityProxy, formaterProxy: LoggingSetupEntityProxy):
        if formaterProxy.name in self._tree['formaters']:
            return

        self._tree['formaters'][formaterProxy.name] = {
            'parentPrinterName': printerProxy.name,

            'formater_class': formaterProxy.classPath,
            'settings': formaterProxy.dump_settings()['settings']
        }

    def set_branch(
        self,
        logger: LoggingSetupEntityProxy,
        handler: LoggingSetupEntityProxy,
        printer: LoggingSetupEntityProxy,
        formater: LoggingSetupEntityProxy
    ):
        self.set_logger(logger)
        self.set_handler(logger, handler)
        self.set_printer(handler, printer)
        self.set_formater(printer, formater)

    def set_config(self, treeConfig: dict):
        """ Установка настроек логирования через словарь с данными

        Args:
            treeConfig (dict): Словарь настроек

        """

        self._tree = treeConfig


class SetupTree(ValidationSetupTree, SetSetupTree):
    """ Интерфейс для настройки логирования """

    def apply(self):
        """ Применить установленные настройки """

        self.validation()
        # print()
        # print()
        # pprint(self._tree)

        loggersController.apply_settings(self._tree)
        storageController.apply_settings(self._tree)

        self.filling_tree()


rloggingSetup = SetupTree()

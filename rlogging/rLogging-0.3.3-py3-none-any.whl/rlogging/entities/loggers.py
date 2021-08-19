
from rlogging.setup.proxy import LoggingSetupEntityProxy
from rlogging import levels
from rlogging.entities.base import BaseLogger


class Logger(BaseLogger):
    """ Интерфейс логера, для создания и передачи логов """

    def debug(self, message: str, **kwargs):
        """ Создать лог уровня debug.

        Args:
            message (str): Сообщение лога
            kwargs (dict): Доп параметры

        """

        self._log(levels.DEBUG_DEFAULT_LOGGING_LEVEL, message, kwargs)

    def info(self, message: str, **kwargs):
        """ Создать лог уровня info.

        Args:
            message (str): Сообщение лога
            kwargs (dict): Доп параметры

        """

        self._log(levels.INFO_DEFAULT_LOGGING_LEVEL, message, kwargs)

    def warning(self, message: str, **kwargs):
        """ Создать лог уровня warning.

        Args:
            message (str): Сообщение лога
            kwargs (dict): Доп параметры

        """

        self._log(levels.WARNING_DEFAULT_LOGGING_LEVEL, message, kwargs)

    def error(self, message: str, **kwargs):
        """ Создать лог уровня error.

        Args:
            message (str): Сообщение лога
            kwargs (dict): Доп параметры

        """

        self._log(levels.ERROR_DEFAULT_LOGGING_LEVEL, message, kwargs)

    def critical(self, message: str, **kwargs):
        """ Создать лог уровня critical.

        Args:
            message (str): Сообщение лога
            kwargs (dict): Доп параметры

        """

        self._log(levels.CRITICAL_DEFAULT_LOGGING_LEVEL, message, kwargs)

    def exception(self, exception: Exception):
        """ Создание лога на основе исключения

        Args:
            exception (Exception): Исключение

        """

        message = '{0} : {1}'.format(
            exception.__class__.__name__,
            exception
        )
        self.critical(message)

    @classmethod
    def setup(cls, **kwargs) -> LoggingSetupEntityProxy:
        """ Создание прокси для настройки логгера Logger

        Args:
            kwargs: Значение полей настроки. Подробнее в Kwargs

        Kwargs:
            name (str): Имя логера, по которому нго можно получить с помощью get_logger
            minLogLevel (str): Минимальный уровень лога, сделанный настраиваемым логерои,
            который будет обрабатываться дальше по цепочке

        Returns:
            LoggingSetupEntityProxy: Прокси настроки логгера Logger

        """

        return super().setup('logger', **kwargs)

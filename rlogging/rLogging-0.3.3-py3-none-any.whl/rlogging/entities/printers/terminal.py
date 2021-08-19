
from rlogging.entities.base import BasePrinter, BaseRecord
from rlogging.setup.proxy import LoggingSetupEntityProxy


class TerminalPrinter(BasePrinter):
    """ Принтер для вывода сообщений в терминал """

    __setup_fields__ = ('colors', )

    colors: dict = {
        'rubbish': '0m',
        'debug': '37m',
        'info': '32m',
        'warning': '33m',
        'error': '31m',
        'critical': '31m',
    }

    @classmethod
    def setup(cls, **kwargs) -> LoggingSetupEntityProxy:
        """ Создание прокси для настройки принтера TerminalPrinter

        Args:
            kwargs: Значение полей настроки. Подробнее в Kwargs

        Kwargs:
            colors (dict[str]): Словарь лейблов уровня лога и цвета этого лога

        Returns:
            LoggingSetupEntityProxy: Прокси настроки принетера FilePrinter

        """

        return super().setup('printer', **kwargs)

    def processing(self, record: BaseRecord, recordString: str):
        recordString = '\033[{0}{1}\033[0m'.format(
            self.colors[record.loggingLevelLabel.lower()],
            recordString
        )
        print(recordString)

from rlogging.entities.base import BasePrinter, BaseRecord
from rlogging.setup.proxy import LoggingSetupEntityProxy
import pathlib as pa


class BaseLogFileChecker(object):

    record: BaseRecord
    logFile: str

    _logFilePath: pa.Path
    _logFolderPath: pa.Path

    def __init__(self, record: BaseRecord, logFile: str) -> None:
        self.record = record
        self.logFile = logFile

        self._logFilePath = pa.Path(logFile)
        self._logFolderPath = pa.Path(logFile).parent

    def create_file(self, logFile: pa.Path):
        """ Создание файла и родительской паки

        Args:
            logFile (pa.Path): Целевой файл

        """

        logFile.parent.mkdir(exist_ok=True)
        logFile.touch(exist_ok=True)

    def separate(self, logFile: pa.Path) -> pa.Path:
        """ Определение необходимости оспользовать другой файл для записи этого лога

        Args:
            logFile (pa.Path): Целевой файл

        Returns:
            pa.Path: Файл в который нужно записать лог

        """

        return logFile

    def get_folder(self) -> pa.Path:
        """ Формирование пути до папки, в которой будет файл, в который будет записываться лог

        Returns:
            pa.Path: Папка, в которой хранятся файла логов

        """

        return self._logFolderPath

    def get_file(self) -> pa.Path:
        """ Формирование объекта файла, в который будет записываться лог

        Returns:
            pa.Path: Файл в который нужно записать лог

        """

        logFile = self._logFilePath

        logFile = self.separate(logFile)

        self.create_file(logFile)

        return logFile


class FilePrinter(BasePrinter):
    """ Принтер для сохранения сообщений в файл """

    fileCheckerClass: type[BaseLogFileChecker] = BaseLogFileChecker

    __setup_fields__ = (
        'logFile',
        # 'writeChunkSize', 'maxFileSize', 'checkFileSize'
    )

    logFile: str = 'rlogging.log'

    writeChunkSize: int = 50
    maxFileSize: int = 83886080
    checkFileSize: int = 50

    @classmethod
    def setup(cls, **kwargs) -> LoggingSetupEntityProxy:
        """ Создание прокси для настройки принтера FilePrinter

        Args:
            kwargs: Значение полей настроки. Подробнее в Kwargs

        Kwargs:
            logFile (str): Расположение файла логов, в который будут писаться логи.
            (no release) writeChunkSize (int): По сколько логов за раз записывать в файл
            (no release) maxFileSize (int): Максимальный размер файла лога
            (no release) checkFileSizeRepear (int): Проверять размкр файла раз в сколько повторений

        Returns:
            LoggingSetupEntityProxy: Прокси настроки принетера FilePrinter

        """

        return super().setup('printer', **kwargs)

    def processing(self, record: BaseRecord, recordString: str):
        fileChecker = self.fileCheckerClass(
            record, self.logFile
        )

        logFile = fileChecker.get_file()
        fileIO = logFile.open('a')
        recordString = '\n{0}'.format(
            recordString
        )
        fileIO.write(recordString)
        fileIO.close()

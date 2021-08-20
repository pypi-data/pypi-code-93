""" Основной модуль пакета rcore -"""

__debug_mod__ = True

import os
import pathlib as pa
import typing as _T

import rlogging

from rcore import cli
from rcore import exception as ex
from rcore import rpath
from rcore.config import cf
from rcore.entrypoint import d_entrypoint

MIN_LOGGING_LEVEL = 20

logger = rlogging.get_logger('mainLogger')


def logging_setup():
    """ Настройка логеров """

    lineFormaterMinInfo = rlogging.entities.formaters.LineFormater.setup()
    lineFormaterMoreInfo = rlogging.entities.formaters.LineFormater.setup()

    terminalPrinter = rlogging.entities.printers.TerminalPrinter.setup()
    filePrinter = rlogging.entities.printers.FilePrinter.setup(
        logFile=str(rpath.rPath('rcore.log', fromPath='logs'))
    )

    mainProcessHandler = rlogging.entities.handlers.MainProcessHandler.setup(
        minLogLevel=60
    )
    subProcessHandler = rlogging.entities.handlers.MainProcessHandler.setup(
        minLogLevel=0
    )

    mainLogger = rlogging.entities.loggers.Logger.setup(
        name='mainLogger',
        minLogLevel=MIN_LOGGING_LEVEL
    )

    rlogging.rloggingSetup.set_branch(mainLogger, mainProcessHandler, terminalPrinter, lineFormaterMinInfo)
    rlogging.rloggingSetup.set_branch(mainLogger, subProcessHandler, filePrinter, lineFormaterMoreInfo)

    rlogging.rloggingSetup.apply()


def set_path(userPath: _T.Union[pa.Path, str],
             projectPath: _T.Optional[_T.Union[pa.Path, str]] = None,
             cacheFolderName: _T.Optional[str] = None,
             logsFolderName: _T.Optional[str] = None
             ):
    """ Инициализация корневых путей приложения

    Args:
        userPath (_T.Union[pa.Path, str]): Рабочая директория пользователя
        projectPath (_T.Union[pa.Path, str, None], optional): Директория надстройки над rcore. Defaults to pa.Path(__file__).parent.
        cacheFolderName (_T.Optional[str], optional): Папка используемая как кеш приложения. Defaults to 'cache'.
        logsFolderName (_T.Optional[str], optional): Папка для хранения логов приложения. Defaults to 'cache/logs'.

    """

    if isinstance(userPath, str):
        userPath = pa.Path(userPath)

    if projectPath is None:
        projectPath = pa.Path(__file__).parent

    elif isinstance(projectPath, str):
        projectPath = pa.Path(projectPath)

    if cacheFolderName is None:
        cacheFolderName = 'cache'

    if logsFolderName is None:
        logsFolderName = 'cache/logs'

    rpath.rPaths.init(
        userPath,
        projectPath,
        pa.Path(__file__).parent,
        cacheFolderName,
        logsFolderName
    )


def set_config(patterns: list = [], files: dict = {}, dictconfig: dict = {}):
    """ Определение файлов конфигурации. """

    cf.init({
        'project': patterns,
        'app': ['*.json']
    }, files, dictconfig)


""" Пример работы с rcore

Функции init и start являются примерами инициализации и запуска программы.
Функцию stop можно вызывать надстройками.

"""


def init():
    """ Инициализация приложения rcore.

    Запуск необходимых функций, процессов, etc.

    """

    logger.info('Инициализация rcore')

    logging_setup()


def stop():
    """ Остановка всех служб rcore """

    logger.info('Остановка всех служб rcore')


@d_entrypoint(stop)
def start():
    """ Запуск основного функционала приложения """

    logger.info('Запуск rcore')

    set_path(os.getcwd(), os.path.dirname(__file__))
    init()

    cli.start()

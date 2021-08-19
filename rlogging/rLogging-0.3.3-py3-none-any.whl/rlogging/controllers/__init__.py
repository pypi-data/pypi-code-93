import multiprocessing as _M

from execution_controller.processes import start_tracking
from rlogging.controllers.loggers import LoggersController
from rlogging.controllers.storage import StorageController

loggersController = LoggersController()
storageController = StorageController()


def start_storage():
    """ Запуск контроллеров """

    executionInProgress = start_tracking()
    logStorageQueue = _M.Queue()
    setupPipe = _M.Pipe()

    loggersController.set(logStorageQueue)

    storageController.set(logStorageQueue, executionInProgress, setupPipe)
    storageController.start()


if _M.current_process().name == 'MainProcess':
    start_storage()

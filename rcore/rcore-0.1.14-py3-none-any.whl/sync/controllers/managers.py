import multiprocessing as _M
from multiprocessing.managers import SyncManager
import typing as _T


class BaseControllerManager(object):
    """ Базовый класс для менеджера контроллера.

    Нужен для обмена очередями между дочерними процессами и воркером

    """

    manager: SyncManager

    inputtedQueue: dict[str, _M.Queue]
    outputtedQueue: dict[str, _M.Queue]
    commonQueue: _M.Queue

    def __init__(self) -> None:
        self.manager = _M.Manager()

        self.inputtedQueue = {}
        self.outputtedQueue = {}
        self.commonQueue = self.manager.Queue(0)

    def queues(self, processKey: str):
        return self.inputtedQueue[processKey], self.outputtedQueue[processKey]

    def set_queues(self, processKey: str):
        if processKey in self.inputtedQueue:
            raise ValueError('Очередь для Процесса с ключом "{0}" уже создана'.format(
                processKey
            ))

        self.inputtedQueue[processKey] = self.manager.Queue(1)
        self.outputtedQueue[processKey] = self.manager.Queue(1)

    def common(self) -> _T.Any:
        """ Получение общей информации об обработанных контроллером данных

        Returns:
            _T.Any: Объект находящийся в очереди

        """

        return self.commonQueue.get()

    def put(self, processKey: str, messageObj: _T.Any):
        self.inputtedQueue[processKey].put(messageObj)

    def get(self, processKey: str):
        self.outputtedQueue[processKey].get()

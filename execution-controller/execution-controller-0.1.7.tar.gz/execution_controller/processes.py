""" Отслеживание работы процессов приложения """

import ctypes
import multiprocessing as _M
import signal
import sys
import time
from multiprocessing.managers import ValueProxy


class RunTimeControllerWorker(object):
    """ Воркер ожидающий пока его убьет родитель """

    executionInProgress: ValueProxy[bool]

    targetSignals: list[signal.Signals] = [
        signal.SIGTERM, signal.SIGINT
    ]

    def __init__(self):
        pass

    def set(self, executionInProgress: ValueProxy[bool]):
        self.executionInProgress = executionInProgress

    def _change_state(self):
        self.executionInProgress.value = False

    def _signal_handle(self):
        def handler(signalNumb, _):
            self._change_state()
            sys.exit(signalNumb)

        for targetSignal in self.targetSignals:
            signal.signal(targetSignal, handler)

    def on_process(self):
        self._signal_handle()

        while True:
            time.sleep(1)


class RunTimeController(object):
    """ Контроллер для запуска процесса-демона, который будет следить за работой основного приложения """

    # Переменная отражающая работает ли процесс, из которого запущен демон, или нет
    executionInProgress: ValueProxy[bool]

    # Воркер контроллера
    worker_class: type[RunTimeControllerWorker] = RunTimeControllerWorker
    worker: RunTimeControllerWorker

    # Процесс-демон
    process: _M.Process

    def __init__(self) -> None:
        self.worker = self.worker_class()

    def set(self, executionInProgress: ValueProxy[bool]):
        """ Установка переменных для обмена данными между процессами

        Args:
            executionInProgress (ValueProxy[bool]): Отслеживание работаеты процесса

        """

        self.worker.set(executionInProgress)

    def start(self):
        """ Запуск дочернего процесса-демона """

        self.process = _M.Process(
            target=self.worker.on_process,
            daemon=True
        )
        self.process.start()


def start_tracking() -> ValueProxy[bool]:
    """ Начать отслеживание работы процесса (основного или дочернего)

    Returns:
        ValueProxy[bool]: Переменная, отражающая работает ли приложение (True) или нет (False)

    """

    executionInProgress = _M.Value(ctypes.c_bool, ValueProxy[bool])

    controller = RunTimeController()
    controller.set(executionInProgress)

    controller.start()

    return executionInProgress

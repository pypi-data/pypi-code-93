from copy import copy, deepcopy
import multiprocessing as _M

from execution_controller.processes import start_tracking
from rlogging import processes
from rlogging.entities.base.handlers import BaseHandler, CoreHandler
from rlogging.entities.base.records import BaseRecord


class SubProcessHandlerWorker(BaseHandler, processes.SubProcessWorker):
    """ Воркер, обрабатывающий логи в своем процессе """

    def processing(self):
        record = self.logQueue.get()
        self.transfer(record)


# class SubProcessHandler(CoreHandler, processes.SubProcessController):
#     """ Хендлер, обрабатывающий логи в дополнительном процессе """

#     worker_class = SubProcessHandlerWorker

#     def __init__(self, name: str):
#         super().__init__(name)
#         self.worker = self.worker_class(self.name)

#         executionInProgress = start_tracking()

#         manager = _M.Manager()
#         self.adadadadadadad = manager.Queue()
#         setupPipe = _M.Pipe()

#         self.set(self.adadadadadadad, executionInProgress, setupPipe)

#     def transfer(self, record: BaseRecord):
#         self.logQueue.put(record)

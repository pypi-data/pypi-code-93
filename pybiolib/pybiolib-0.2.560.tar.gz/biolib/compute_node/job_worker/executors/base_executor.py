import abc

from biolib.compute_node.job_worker.executors.types import LocalExecutorOptions


class BaseExecutor(abc.ABC):

    def __init__(self, options: LocalExecutorOptions):
        self._options: LocalExecutorOptions = options

    @abc.abstractmethod
    def execute_module(self, module_input_serialized: bytes) -> bytes:
        pass

from abc import ABC, abstractmethod
from prunner.util import shellexpand


class TaskStrategy(ABC):
    def modify_params(self, params, variables=None):
        return shellexpand(params, variables)

    @abstractmethod
    def execute(self, params, variables=None):
        pass

    @classmethod
    def from_settings(cls, settings):
        return cls()

    @classmethod
    def task_name(cls):
        return ""

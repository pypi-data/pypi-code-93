from abc import ABC, abstractmethod


class ModuleProvider(ABC):

    @abstractmethod
    def get_instance(self, **kwargs):
        pass


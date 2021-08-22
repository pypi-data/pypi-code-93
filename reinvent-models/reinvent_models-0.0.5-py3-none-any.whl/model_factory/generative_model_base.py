from abc import ABC, abstractmethod


class GenerativeModelBase(ABC):

    @abstractmethod
    def load_from_file(self, path_to_file, mode: str = 'training'):
        raise NotImplemented("load_from_file method is not implemented")

    @abstractmethod
    def save_to_file(self, path_to_file: str):
        raise NotImplemented("save_to_file method is not implemented")

    @abstractmethod
    def likelihood(self, *args, **kwargs):
        raise NotImplemented("likelihood method is not implemented")

    @abstractmethod
    def sample(self, *args, **kwargs):
        raise NotImplemented("sample method is not implemented")
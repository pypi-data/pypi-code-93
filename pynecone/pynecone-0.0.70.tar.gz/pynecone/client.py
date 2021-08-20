from abc import ABC, abstractmethod
from .config import Config


class Client(ABC):

    def __init__(self):
        self.cfg = Config.init()

    def get_config(self):
        return self.cfg

    @abstractmethod
    def run(self, args):
        pass

    @abstractmethod
    def get_client(self):
        pass

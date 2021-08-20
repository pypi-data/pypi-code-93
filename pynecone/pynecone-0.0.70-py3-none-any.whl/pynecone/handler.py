from abc import ABC, abstractmethod


class Handler(ABC):

    def __init__(self, name):
        self.name = name

    @abstractmethod
    def get_blueprint(self):
        pass

    def get_route_name(self):
        return self.name

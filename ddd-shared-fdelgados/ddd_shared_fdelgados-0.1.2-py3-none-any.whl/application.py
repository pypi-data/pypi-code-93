import abc


class Command:
    pass


class CommandHandler(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        if subclass is not CommandHandler:
            return NotImplementedError

        if hasattr(subclass, "handle") and callable(subclass.handle):
            return True

        return NotImplementedError

    @abc.abstractmethod
    def handle(self, command: Command, **kwargs) -> None:
        raise NotImplementedError


class Query:
    pass


class Response:
    pass


class QueryHandler(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        if subclass is not QueryHandler:
            return NotImplementedError

        if hasattr(subclass, "handle") and callable(subclass.handle):
            return True

        return NotImplementedError

    @abc.abstractmethod
    def handle(self, query: Query, **kwargs) -> Response:
        raise NotImplementedError

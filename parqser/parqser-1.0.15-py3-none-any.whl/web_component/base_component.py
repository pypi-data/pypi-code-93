from typing import Any


class BaseComponent:
    def __init__(self):
        self.name = self._camel_to_snake_case(self.__class__.__name__)

    def _camel_to_snake_case(self, name: str) -> str:
        camel2snake = lambda c: c if c.islower() else '_' + c.lower()
        name = ''.join(list(map(camel2snake, name)))
        if name.startswith('_'):
            name = name[1:]
        return name

    def xpath(self, elem):
        return elem.getroottree().getpath(elem)

    def parse(self, source: str) -> Any:
        """Fetches data from source html"""
        raise NotImplemented

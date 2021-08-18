from typing import Any, Callable, Dict

from native_rpc.exceptions import FuncNotFoundException, ClassNotFoundException


class Namespace:
    def __init__(self, name: str = 'default'):
        self._name = name
        self._remote_func: Dict[str, Callable] = {}
        self._remote_class: Dict[str, Any] = {}

    def __repr__(self):
        return f'<{type(self).__name__} {self._name}: {len(self._remote_func)} functions, {len(self._remote_class)} classes>'

    @property
    def name(self) -> str:
        return self._name

    def get_remote_func(self, name: str) -> Callable:
        func = self._remote_func.get(name)
        if func is None:
            raise FuncNotFoundException(name)
        return func

    def get_remote_class(self, name: str) -> Any:
        cls = self._remote_class.get(name)
        if cls is None:
            raise ClassNotFoundException(name)
        return cls

    def add_remote_func(self, name: str, func: Callable):
        self._remote_func[name] = func

    def add_remote_class(self, name: str, cls: Any):
        self._remote_class[name] = cls

    def merge(self, ns: 'Namespace'):
        self._remote_func = {**self._remote_func, **ns._remote_func}
        self._remote_class = {**self._remote_class, **ns._remote_class}

    def remote_func(self, name: str = None):
        def decorator(func):
            nonlocal name
            if name is None:
                name = func.__name__
            self.add_remote_func(name, func)
            return func

        return decorator

    def remote_class(self, name: str = None):
        def decorator(cls):
            nonlocal name
            if name is None:
                name = cls.__name__
            self.add_remote_class(name, cls)
            return cls

        return decorator

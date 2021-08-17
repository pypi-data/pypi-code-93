from typing import TypeVar, Union, Callable, Any, Optional


T = TypeVar("T")


class MetaCheck:
    def __init__(self, fget: Callable[[Any], bool], doc: str = None) -> None:
        self.fget = fget
        if doc is None:
            doc = fget.__doc__
        self.__doc__ = doc

    def __get__(self, obj: Optional[T], type: Optional[T]) -> Union[bool, "MetaCheck"]:
        if obj is None:
            return self
        return self.fget(obj)

    def __set__(self, obj, value) -> None:
        raise AttributeError("Cannot change the value")

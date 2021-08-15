import inspect
import sys
import typing
from abc import ABCMeta
from dataclasses import MISSING, InitVar, is_dataclass
from typing import List, Type, TypedDict, Union

assert (3, 8) <= sys.version_info < (3, 11), f"{sys.version} is not compatible with this package"

if sys.version_info < (3, 9):  # pragma: no cover
    import typing_extensions
    from typing_extensions import Annotated
    AnnotatedAlias = getattr(typing_extensions, "_AnnotatedAlias")
    _BaseGenericAlias = _GenericAlias = _SpecialGenericAlias = getattr(typing, "_GenericAlias")
    GenericAlias = NotImplemented
else:  # pragma: no cover
    from types import GenericAlias
    from typing import Annotated
    AnnotatedAlias = getattr(typing, "_AnnotatedAlias")
    _BaseGenericAlias = getattr(typing, "_BaseGenericAlias")
    _GenericAlias = getattr(typing, "_GenericAlias")
    _SpecialGenericAlias = getattr(typing, "_SpecialGenericAlias")
    assert type(list[str]) is GenericAlias, (type(list[str]), GenericAlias)

assert type(Annotated[str, ""]) is AnnotatedAlias, (type(Annotated[str, ""]), AnnotatedAlias)
assert type(List) is _SpecialGenericAlias, (type(List), _SpecialGenericAlias)
assert type(List[str]) is _GenericAlias, (type(List[str]), _GenericAlias)

_TypedDictMeta = type(TypedDict("", {}))


def _is_annotated_class(subclass, /):
    return isinstance(subclass, type) and isinstance(getattr(subclass, "__annotations__", None), dict)


class Empty:

    def __repr__(self):
        return "<empty>"


TEmpty = Union[Type[inspect.Parameter.empty], Empty, type(MISSING)]

empty = Empty()


class GenericAliasProto(metaclass=ABCMeta):
    _valid_bases = tuple(filter(lambda x: x is not NotImplemented, (_BaseGenericAlias, GenericAlias)))

    @classmethod
    def __subclasshook__(cls, subclass, /):
        return isinstance(subclass, type) and issubclass(subclass, cls._valid_bases)


class NamedClassProto(metaclass=ABCMeta):
    __valid_bases = ()

    @classmethod
    def register_base(cls, subclass: type, /):
        assert cls is NamedClassProto and subclass not in cls.__valid_bases, (cls, subclass, cls.__valid_bases)
        cls.__valid_bases = (*cls.__valid_bases, subclass)
        return subclass

    @classmethod
    def __subclasshook__(cls, subclass, /):
        return _is_annotated_class(subclass) and issubclass(subclass, cls.__valid_bases)


register_named_class = getattr(NamedClassProto, "register_base")


@register_named_class
class NamedTupleProto(metaclass=ABCMeta):

    @classmethod
    def __subclasshook__(cls, subclass, /):
        return _is_annotated_class(subclass) and issubclass(subclass, tuple) and hasattr(subclass, "_fields")


class DataClassProto(metaclass=ABCMeta):

    @classmethod
    def __subclasshook__(cls, subclass, /):
        return _is_annotated_class(subclass) and is_dataclass(subclass)


@register_named_class
class ValidDataClassProto(metaclass=ABCMeta):

    @classmethod
    def __subclasshook__(cls, subclass, /):
        return (
            issubclass(subclass, DataClassProto) and not any(
                map(
                    lambda f: (isinstance(f.type, InitVar) and f.default is MISSING and f.default_factory is MISSING),
                    subclass.__dataclass_fields__.values()
                )
            )
        )


@register_named_class
class TypedDictProto(metaclass=ABCMeta):

    @classmethod
    def __subclasshook__(cls, subclass, /):
        return _is_annotated_class(subclass) and subclass is not TypedDict and isinstance(subclass, _TypedDictMeta)


class ForwardRefProto:
    __forward_arg__: str


def as_forward_ref(instance, /):
    if isinstance(getattr(instance, "__forward_arg__", None), str):
        return instance
    raise TypeError(instance)

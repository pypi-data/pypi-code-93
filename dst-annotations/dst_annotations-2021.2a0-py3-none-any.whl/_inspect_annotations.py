import sys
import typing

from ._annotations import AnnotatedAlias, TypedDictProto

if sys.version_info >= (3, 9):  # pragma: no cover
    from types import GenericAlias
    _BaseGenericAlias = getattr(typing, "_BaseGenericAlias")
else:  # pragma: no cover
    GenericAlias = NotImplemented
    _BaseGenericAlias = getattr(typing, "_GenericAlias")

NoneType: typing.Type[None] = type(None)  # ToDo 3.10 includes NoneType in types module


def get_runtime_types(obj) -> typing.Tuple[type, ...]:
    if isinstance(obj, typing.ForwardRef) or obj in (typing.Generic, typing.Optional, typing.TypedDict):
        raise TypeError(f"{obj}: runtime type unknown")
    if isinstance(obj, type) and getattr(obj, "_is_protocol", False):
        raise TypeError(f"{obj}: runtime type unknown")
    if isinstance(obj, AnnotatedAlias):
        return get_runtime_types(obj.__args__[0])
    if isinstance(obj, typing.TypeVar):
        return get_runtime_types(typing.Union[obj.__constraints__ or obj.__bound__ or object])
    if obj in (typing.Any, typing.ClassVar, typing.Final):
        return object,
    if obj in (None, NoneType, typing.NoReturn):
        return NoneType,
    origin = typing.get_origin(obj)
    if origin is None:
        if not isinstance(obj, type):
            raise TypeError(f"{obj}: runtime type unknown")
        if issubclass(obj, TypedDictProto):  # type: ignore
            return dict,
        return obj,
    if GenericAlias is not NotImplemented and isinstance(obj, GenericAlias):
        return origin,
    if origin is typing.Literal:
        return tuple(sorted({type(x) for x in obj.__args__}, key=str))  # yapf: disable
    if origin is typing.ClassVar or origin is typing.Final:
        return get_runtime_types(obj.__args__[0])
    if origin is typing.Union:
        runtime_types: typing.List[type] = []
        for items in (get_runtime_types(arg) for arg in obj.__args__ if arg is not NoneType):
            runtime_types.extend(item for item in items if item not in runtime_types)
        if float in runtime_types and int not in runtime_types:
            runtime_types = [*runtime_types, int]
        if NoneType in obj.__args__:
            runtime_types.append(NoneType)
        return tuple(runtime_types)
    if isinstance(obj, _BaseGenericAlias):
        return origin,
    raise TypeError(f"{obj}: runtime type unknown")  # pragma: no cover

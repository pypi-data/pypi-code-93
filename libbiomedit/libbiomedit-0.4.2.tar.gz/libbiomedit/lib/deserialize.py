from typing import Union, Tuple, Any, Dict, Optional, Sequence, cast, Callable, Type
import collections
import warnings
from enum import Enum

import dataclasses

from .classify import classify, __origin_attr__, AbstractType, IsDataclass, IsTypingType


def deserialize(T: AbstractType) -> Callable[[Any], Any]:
    """Creates a deserializer for the type :T:. It handles dataclasses,
    sequences, typing.Optional, Enum and primitive types.

    :returns: A deserializer, converting a dict, list or primitive to :T:
    """
    return _deserializers.get(classify(T), lambda x: x)(T)


def serialize(T: AbstractType) -> Callable[[Any], Any]:
    """Creates a serializer for the type :T:. It handles dataclasses,
    sequences, typing.Optional, Enum and primitive types.

    :returns: A serializer, converting an instance of :T: to dict, list or primitive
    """
    return _serializers.get(classify(T), lambda x: x)(T)


_deserializers = {}
_serializers = {}


def _deserializer(T: Any):
    def decorator(f):
        _deserializers[T] = f
        return f

    return decorator


def _serializer(T: Any):
    def decorator(f):
        _serializers[T] = f
        return f

    return decorator


def _serializer_deserializer(T: Any):
    def decorator(f):
        _deserializers[T] = f(deserialize)
        _serializers[T] = f(serialize)
        return f

    return decorator


@_serializer(Any)
@_deserializer(Any)
def transform_any(_: AbstractType):
    return lambda x: x


@_serializer_deserializer(Tuple)
def transform_tuple(transform):
    def _transform_tuple(T: IsTypingType):
        item_types = cast(Tuple[AbstractType, ...], T.__args__)
        if len(item_types) == 2 and item_types[1] is ...:
            item_type = item_types[0]

            def _transform_ellipsis(data: tuple):
                return tuple(transform(item_type)(item) for item in data)

            return _transform_ellipsis

        def _transform(data: tuple):
            if len(item_types) != len(data):
                raise ValueError(f"Wrong number ({len(data)}) of items for {repr(T)}")
            return tuple(transform(T)(item) for T, item in zip(item_types, data))

        return _transform

    return _transform_tuple


@_serializer_deserializer(Sequence)
def transform_seq(transform):
    def _transform_seq(T: IsTypingType):
        seq_type = getattr(T, __origin_attr__, None)
        try:
            item_type = T.__args__[0]
        except AttributeError as e:
            raise ValueError(
                f"Sequence of type {seq_type.__name__} without item type"
            ) from e
        if seq_type is collections.abc.Sequence:
            seq_type = list

        def _transform(data):
            return seq_type(map(transform(item_type), data))

        return _transform

    return _transform_seq


@_deserializer(IsDataclass)
def deserialize_dataclass(T):
    fields = dataclasses.fields(T)

    def _deserialize(data: dict):
        unexpected_keys = set(data.keys()) - set(f.name for f in fields)
        if unexpected_keys:
            warnings.warn(
                f"{T.__name__}: Unexpected keys: " + ", ".join(unexpected_keys)
            )
        converted_data = {
            f.name: deserialize(get_deserialize_method(f))(data[f.name])
            for f in fields
            if f.name in data
        }
        return T(**converted_data)

    return _deserialize


def get_deserialize_method(f: dataclasses.Field) -> type:
    return f.metadata.get("deserialize", f.type)


@_serializer(IsDataclass)
def serialize_dataclass(T):
    fields = dataclasses.fields(T)

    def _serialize(obj):
        converted_data = {
            f.name: serialize(get_serialize_method(f))(getattr(obj, f.name))
            for f in fields
        }
        return converted_data

    return _serialize


def get_serialize_method(f: dataclasses.Field) -> type:
    return f.metadata.get("serialize", f.type)


@_serializer_deserializer(Optional)
def transform_optional(transform):
    def _transform_optional(T: IsTypingType):
        T1, T2 = T.__args__
        if isinstance(None, T1):
            opt_type = T2
        else:
            opt_type = T1

        def _transform(data):
            if data is None:
                return None
            return transform(opt_type)(data)

        return _transform

    return _transform_optional


@_serializer_deserializer(Union)
def transform_union(transform):
    def _transform_union(T: IsTypingType):
        types = T.__args__

        def _transform(data):
            types_by_name = {t.__name__: t for t in types}
            type_name = data.get("type")
            if type_name is None:
                raise ValueError(
                    f"Union[{', '.join(types_by_name)}]: missing `type` item"
                )
            T = types_by_name.get(type_name)
            if T is None:
                raise ValueError(
                    f"Union[{', '.join(types_by_name)}]: "
                    f"unexpected type `{type_name}`"
                )
            return transform(T)(data["arguments"])

        return _transform

    return _transform_union


@_serializer_deserializer(Dict)
def transform_dict(transform):
    def _transform_dict(T: IsTypingType):
        key_type, val_type = T.__args__

        def _transform(data):
            return {
                transform(key_type)(key): transform(val_type)(val)
                for key, val in data.items()
            }

        return _transform

    return _transform_dict


@_serializer(Enum)
def serialize_enum(_T: Type[Enum]):
    def _serialize(obj: Enum):
        return obj.value

    return _serialize

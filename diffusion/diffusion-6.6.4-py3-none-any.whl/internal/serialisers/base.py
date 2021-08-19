""" Base classes for implementation of serialisers. """

from __future__ import annotations

import io
from typing import Any, cast, Iterable, List, Mapping, MutableMapping, Sequence, Dict

import structlog
from stringcase import pascalcase, snakecase

from diffusion.internal.encoded_data import Byte, EncodingType, is_encoder
from diffusion.internal.utils import flatten_mapping
from .compound import MapSerialiser, ScalarSetSerialiser
from .spec import SERIALISER_SPECS, SerialiserMap, NULL_VALUE_KEY, Compound, CompoundSpec

LOG = structlog.get_logger()


class Serialiser:
    """ Class for individual serialisers. """

    def __init__(self, name: str, spec: SerialiserMap):
        self.name = name
        self.spec = spec

    def from_bytes(self, value: bytes):
        """ Deserialise a bytes value. """
        yield from self.read(io.BytesIO(value))

    def read(self, stream: io.BytesIO):
        """ Read the value from a binary stream. """
        yield from self._recurse_read(self.spec.values(), stream)

    def _recurse_read(self, types, stream):
        types = tuple(flatten_mapping(types))
        for item in types:
            if is_encoder(item):
                yield item.read(stream).value
            elif item is not None:
                yield tuple(self._recurse_read(item, stream))
            else:
                yield None

    def to_bytes(self, *values) -> bytes:
        """ Serialise the value into bytes. """
        return self._recurse_write(self.spec.values(), values)

    def write(self, stream: io.BytesIO, *values) -> io.BytesIO:
        """ Write the value into a binary stream. """
        stream.write(self.to_bytes(*values))
        return stream

    def _recurse_write(self, types, values):
        result = b""
        types = tuple(flatten_mapping(types))
        for item, value in zip(types, values):
            if is_encoder(item):
                result += item(value).to_bytes()
            elif item is not None and isinstance(value, Iterable):
                result += self._recurse_write(item, value)
        return result

    def __iter__(self):
        return iter(self.spec.items())

    @property
    def fields(self):
        """ Returns a list of all the field names. """
        return list(self.spec)

    def __repr__(self):
        return f"<{type(self).__name__} name={self.name}>"

    @classmethod
    def by_name(cls, name: str = NULL_VALUE_KEY) -> Serialiser:
        """ Retrieve a serialiser instance based on the spec name. """
        return Serialiser(name, resolve(name))

    def __bool__(self):
        return self.name != NULL_VALUE_KEY


class ChoiceEncodingType(type):
    """ Metaclass for choice encoding types. """

    _choice_encoding_types: Dict[str, ChoiceEncodingType] = {}

    def __new__(mcs, name: str, specs: SerialiserMap) -> ChoiceEncodingType:
        """ Construct a new choice encoder based on the serialiser specs. """
        if name not in mcs._choice_encoding_types:
            serialisers: MutableMapping[int, Serialiser] = {}
            for key, value in specs.items():
                if not (isinstance(key, int) and isinstance(value, Sequence)):
                    raise ValueError(
                        "Keys have to be integers and values have to be sequences."
                    )
                serialiser_name = f"{name}.{key}"
                if all(map(is_encoder, value)):
                    spec = value
                else:
                    spec = tuple(resolve(val) for val in value)
                serialisers[key] = Serialiser(serialiser_name, {serialiser_name: spec})
            class_name = f"{pascalcase(snakecase(name))}ChoiceEncoder"
            new_type = cast(
                ChoiceEncodingType,
                type(class_name, (ChoiceEncoder,), {"serialisers": serialisers}),
            )
            mcs._choice_encoding_types[name] = new_type
        return mcs._choice_encoding_types[name]


class ChoiceEncoder(EncodingType):
    """ Special "encoding type" for choice-based values (i.e. `one-of'). """

    serialisers: Mapping[int, Serialiser]

    def __init__(self, value: Sequence):
        super().__init__(value)

    @classmethod
    def read(cls, stream: io.BytesIO) -> EncodingType:
        """Read the encoded value from a binary stream.

        It converts the read value to the correct type and constructs a new
        instance of the encoding type.
        """
        choice = Byte.read(stream).value
        serialiser = cls.serialisers[choice]
        values: tuple = tuple(*cast(Iterable, serialiser.read(stream)))
        LOG.debug("Read choice values.", serialiser=serialiser, choice=choice, values=values)
        return cls((choice, *values))

    def to_bytes(self) -> bytes:
        """ Convert the value into its bytes representation. """
        result = Byte(self.choice).to_bytes()
        result += self.serialiser.to_bytes(self.values)
        return result

    @property
    def choice(self):
        """ Return the current value of the choice. """
        return self.value[0]

    @property
    def values(self):
        """ Return the current collection of values. """
        return self.value[1:]

    @property
    def serialiser(self):
        """ Return the serialises spec for the current choice. """
        return self.serialisers[self.choice]

    @classmethod
    def from_name(cls, serialiser_name: str) -> ChoiceEncodingType:
        """ Instantiate the class by resolving the serialiser name. """
        return ChoiceEncodingType(serialiser_name, resolve(serialiser_name))


def resolve(serialiser_name: str, parents: List[str] = None) -> SerialiserMap:
    """Extract the serialiser types for any serialiser key in the spec.

    The `parents` argument is used internally to carry the list of all
    recursive parents, which is eventually concatenated to an internal key.

    The name must be a key in the serialiser spec. The value for a key is
    recursively expanded into a mapping of encoding type classes.
    """
    result: SerialiserMap = {}
    if parents is None:
        parents = []
    parents.append(serialiser_name)
    spec: Any = SERIALISER_SPECS[serialiser_name]
    if not (spec is None or is_encoder(spec)):
        if isinstance(spec, str) or not isinstance(spec, Sequence):
            spec = [spec]
        if isinstance(spec, CompoundSpec):
            spec = _resolve_compound(serialiser_name, spec)
        elif not all(map(is_encoder, spec)):
            for value in spec:
                if isinstance(value, CompoundSpec):
                    name = ".".join(parents)
                    result[name] = _resolve_compound(name, value)
                else:
                    result.update(resolve(value, parents.copy()))
            return result
    return {".".join(parents): spec}


def _resolve_compound(name, spec: CompoundSpec):
    # this is where proper pattern matching would come in handy :)
    if spec.type is Compound.MAP_OF:
        return MapSerialiser(
            *(SERIALISER_SPECS.get(sp, sp) for sp in spec.args)  # type: ignore
        )
    if spec.type is Compound.SET_OF:
        set_spec = spec.args[0]
        return ScalarSetSerialiser(SERIALISER_SPECS.get(set_spec, set_spec))  # type: ignore
    if spec.type is Compound.ONE_OF:
        return ChoiceEncodingType(name, spec.args[0])

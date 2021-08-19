from enum import IntEnum

from stringcase import spinalcase

from diffusion.internal.serialisers import get_serialiser, Serialiser


class UpdateConstraintType(IntEnum):

    UNCONSTRAINED_CONSTRAINT = 0
    CONJUNCTION_CONSTRAINT = 1
    BINARY_VALUE_CONSTRAINT = 2
    NO_VALUE_CONSTRAINT = 3
    LOCKED_CONSTRAINT = 4
    NO_TOPIC_CONSTRAINT = 5
    PARTIAL_JSON_CONSTRAINT = 6

    @property
    def serialiser(self) -> Serialiser:
        return get_serialiser(spinalcase(self.name.lower()))


class UpdateConstraint:
    def __init__(self, type: UpdateConstraintType, *values):
        self.type = type
        self.values = values

    def __eq__(self, other):
        try:
            return self.type == other.type and self.values == other.values
        except AttributeError:
            return False

    def to_bytes(self):
        return self.type.serialiser.to_bytes(*self.values)

    def __iter__(self):
        yield self.type
        yield from self.values

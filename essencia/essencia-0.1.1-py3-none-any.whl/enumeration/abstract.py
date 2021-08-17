'''
Abstract enumeration model
'''

__all__ = ['TupleEnum', 'StrEnum']

from enum import (Enum, IntEnum)


class BaseIntEnum(IntEnum):
    pass

class TupleEnum(tuple, Enum):

    @property
    def integer(self):
        return self.value[ 0 ]

    @property
    def word(self):
        return self.value[ 1 ]

    @property
    def subphrase(self):
        return self.value[ 2 ]

    @property
    def phrase(self):
        return self.value[ 3 ]


class StrEnum(str, Enum):
    def __str__(self):
        return self.value


class IntEnum(int, Enum):
    def __str__(self):
        return self.name.lower()
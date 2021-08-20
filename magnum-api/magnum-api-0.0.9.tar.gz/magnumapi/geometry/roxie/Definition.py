from dataclasses import dataclass
from abc import ABC, abstractmethod


@dataclass
class Definition(ABC):
    """Base class for a definition.

       Attributes:
           name (str): The name of a definition (serves as a primary key).
           comment (str): The comment.

    """
    name: str
    comment: str

    @staticmethod
    @abstractmethod
    def get_magnum_to_roxie_dct():
        raise NotImplementedError('This method is not implemented for this class')

    @classmethod
    def get_roxie_to_magnum_dct(cls):
        return {val: key for key, val in cls.get_magnum_to_roxie_dct().items() if val is not None}

    @classmethod
    def reorder_dct(cls, dct: dict) -> dict:
        for key in cls.get_magnum_to_roxie_dct().keys():
            dct[key] = dct.pop(key)
        return dct

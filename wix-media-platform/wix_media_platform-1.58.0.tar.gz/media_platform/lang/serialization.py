from abc import ABC, abstractmethod
from typing import Dict


class Serializable(ABC):

    @abstractmethod
    def serialize(self) -> Dict:
        pass


class Deserializable(ABC):

    @classmethod
    @abstractmethod
    def deserialize(cls, data: Dict):
        pass

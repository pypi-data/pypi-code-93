from abc import ABC, abstractmethod
from uuid import UUID, uuid4


class Entity(ABC):
    id: UUID = uuid4()

    @abstractmethod
    def as_dict(self):
        raise NotImplementedError

    def get_id(self) -> UUID:
        return self.id

from dataclasses import dataclass
from AsteriskRealtimeData.domain.entity import Entity


@dataclass
class QueueStatus(Entity):
    status_code: str
    description: str

    def get_status_code(self) -> int:
        return self.status_code

    def get_description(self) -> str:
        return self.description

    def as_dict(self) -> dict:
        return self.__repr__()

    def __repr__(self):
        return {
            "id": self.get_id(),
            "status_code": self.get_status_code(),
            "description": self.get_description(),
        }

from AsteriskRealtimeData.domain.entity import Entity
from dataclasses import dataclass


@dataclass
class PauseReason(Entity):
    pause_code: str = "000000"
    description: str = "Sin estado"
    paused: bool = False

    def get_pause_code(self) -> str:
        return self.pause_code

    def get_description(self) -> str:
        return self.description

    def is_paused(self):
        return self.paused

    def as_dict(self) -> dict:
        return self.__repr__()

    def __repr__(self):
        return {
            "id": self.get_id(),
            "pause_code": self.get_pause_code(),
            "description": self.get_description(),
            "paused": self.is_paused(),
        }

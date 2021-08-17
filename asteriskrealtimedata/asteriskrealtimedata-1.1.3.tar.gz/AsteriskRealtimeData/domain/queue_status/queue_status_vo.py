from dataclasses import dataclass


@dataclass
class QueueStatusVo:
    status_code: str
    description: str

    def as_dict(self) -> dict:
        return self.__repr__()

    def __repr__(self):
        return {"status_code": self.status_code, "description": self.description}

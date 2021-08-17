from dataclasses import dataclass


@dataclass
class PauseReasonVo:
    pause_code: str
    description: str
    paused: bool

    def as_dict(self):
        return {
            "pause_code": self.pause_code,
            "description": self.description,
            "paused": self.paused,
        }

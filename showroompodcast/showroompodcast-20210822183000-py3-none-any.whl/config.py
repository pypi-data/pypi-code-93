"""Configuration."""
from dataclasses import dataclass, field
from typing import List

from dataclasses_json import DataClassJsonMixin
from yamldataclassconfig.config import YamlDataClassConfig


@dataclass
class SlackConfig(DataClassJsonMixin):
    """This class implements configuration for Slack."""

    bot_token: str
    channel: str


@dataclass
class Config(YamlDataClassConfig):
    """Configuration."""

    # Reason: To use auto complete
    number_process: int = None  # type: ignore
    stop_if_file_exists: bool = None  # type: ignore
    list_room_id: List[int] = field(default_factory=list)
    slack: SlackConfig = field(  # type: ignore
        default=None, metadata={"dataclasses_json": {"mm_field": SlackConfig}}
    )

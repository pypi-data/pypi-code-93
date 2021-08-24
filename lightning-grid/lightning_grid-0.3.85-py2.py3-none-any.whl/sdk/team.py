from dataclasses import dataclass
import datetime
from typing import Dict

from grid.sdk.user import User


@dataclass(frozen=True)
class Team:
    team_id: str
    name: str
    created_at: datetime.datetime
    role: str
    members: Dict[str, User]

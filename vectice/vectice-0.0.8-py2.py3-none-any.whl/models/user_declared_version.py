from dataclasses import dataclass
from typing import Optional


@dataclass
class UserDeclaredVersion:
    userVersion: str
    """"""
    name: Optional[str]
    """"""
    uri: Optional[str] = None
    """"""
    description: Optional[str] = None
    """"""

from typing import Optional


class NameConflictException(Exception):
    """Raised when two names are provided that do not match"""

    def __init__(self, name1: str, name2: str, message: Optional[str] = None):
        self.name1, self.name2 = name1, name2
        super().__init__(message or f"Names {name1} and {name2} do not match")

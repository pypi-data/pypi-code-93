from typing import Optional, Any

from ezcliy.exceptions import MissingPositional


class Positional:
    """Asign value (by source order) to object, allows asking for value or provide default one."""
    value: str = None
    """Fetched value by positional"""

    description: str = None
    """Description for help"""

    def __init__(self, name: str, ask_if_missing: Optional[str] = None, optional: Optional[Any] = None):
        self.name = name
        self.ask_if_missing = ask_if_missing
        self.optional = optional

    def pass_values(self, values: list[str], position: int):
        try:
            self.value = values[position]
        except IndexError:
            if self.ask_if_missing:
                self.value = input(self.ask_if_missing + ": ").strip()
            elif self.optional is not None:
                self.value = self.optional
            else:
                raise MissingPositional(self, position)

    def __repr__(self):
        return f'<Positional expecting {self.name}>'

    def __str__(self):
        return self.value

    def __int__(self):
        return int(self.value)

    def __float__(self):
        return float(self.value)

    def __bool__(self):
        return bool(self.value)

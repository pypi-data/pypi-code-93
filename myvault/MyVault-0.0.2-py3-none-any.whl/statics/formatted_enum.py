from enum import Enum


class FormattedEnum(Enum):
    def formatted(self, **kwargs) -> str:
        return self.value.format(**kwargs)

    def __str__(self) -> str:
        return self.value

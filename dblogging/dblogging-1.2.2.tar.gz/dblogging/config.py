from abc import abstractmethod
from typing import List


class LogTag:
    def __init__(self, name: str, value: int, html_color: str = None):
        self.name = name
        self.alias = ''.join([c.lower() for c in name if c.isalpha()])
        self.value = value
        self.html_color = html_color


class LogTagTemplate:
    default = LogTag(
        name='Default',
        value=0,
        html_color='limegreen'
    )

    critical = LogTag(
        name='Critical',
        value=90,
        html_color='red'
    )

    @classmethod
    def get_all(cls) -> List[LogTag]:
        return [ll for item in dir(cls) if isinstance(ll := getattr(cls, item), LogTag)]


class LogTags(LogTagTemplate):
    pass

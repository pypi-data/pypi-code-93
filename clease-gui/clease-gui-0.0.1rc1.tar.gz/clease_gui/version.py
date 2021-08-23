# pylint: disable=invalid-name
from typing import NamedTuple

__all__ = ('__version__', 'version_info')


class Version(NamedTuple):
    major: int
    minor: int
    micro: int
    tag: str = None

    def __str__(self) -> str:
        """The full version as X.Y.Z-tag"""
        s = f'{self.major}.{self.minor}.{self.micro}'
        if self.tag is not None:
            s += f'-{self.tag}'
        return s

    def short_version(self) -> str:
        """The short X.Y version"""
        return f'{self.major}.{self.minor}'


version_info = Version(0, 0, 1, tag='c1')

__version__ = str(version_info)

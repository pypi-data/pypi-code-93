from abc import ABC, abstractmethod, abstractproperty
from pathlib import Path
from typing import List

from ..config import Config


class Linter(ABC):
    def __init__(self, config: Config) -> None:
        pass

    @abstractmethod
    def run(self, paths: List[Path]) -> List[str]:
        pass

    @abstractproperty
    def dump_config(self, dst: Path) -> None:
        pass

    @abstractproperty
    def name(self) -> str:
        pass

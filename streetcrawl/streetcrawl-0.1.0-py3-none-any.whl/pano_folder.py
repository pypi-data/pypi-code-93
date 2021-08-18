from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Tuple

from streetcrawl.pano import ImgRequest


class PanoFolder(ABC):
    @abstractmethod
    def save(self, pics: List[Tuple[bytes, ImgRequest]]) -> List[Path]:
        pass

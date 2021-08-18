from pathlib import Path
from typing import List, Tuple

from streetcrawl.pano import ImgRequest
from streetcrawl.pano_folder import PanoFolder


class PanoFolderSimple(PanoFolder):
    def __init__(self, directory: Path, pano_id: str):
        self._dir: Path = directory
        self._pano: str = pano_id

    def save(self, pics: List[Tuple[bytes, ImgRequest]]) -> List[Path]:
        return [self.save_one(pic, rq) for pic, rq in pics]

    def save_one(self, pic: bytes, rq: ImgRequest) -> Path:
        folder = self._dir / self._pano
        folder.mkdir(parents=True, exist_ok=True)
        name = f"{rq.fov}-{rq.heading}.jpg"
        with open(folder / name, "wb") as f:
            f.write(pic)
        return folder / name

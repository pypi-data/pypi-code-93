import io
from pathlib import Path
from typing import List, Tuple

from PIL import Image

from streetcrawl.pano import ImgRequest
from streetcrawl.pano_folder import PanoFolder


class PanoFolderGlued(PanoFolder):
    def __init__(self, directory: Path, pano_id: str, duplicate_on_seams: bool = False):
        self._dir: Path = directory
        self._pano: str = pano_id
        self._dup_on_seams: bool = duplicate_on_seams

    def save(self, pics: List[Tuple[bytes, ImgRequest]]) -> List[Path]:
        pics = self._seams_handled(self._sorted(pics))
        images = [Image.open(io.BytesIO(bts)) for bts, rq in pics]
        widths, heights = zip(*(i.size for i in images))
        total_width = sum(widths)
        max_height = max(heights)
        new_im = Image.new("RGB", (total_width, max_height))
        x_offset = 0
        for im in images:
            new_im.paste(im, (x_offset, 0))
            x_offset += im.size[0]
        return self._save(new_im, pics)

    @staticmethod
    def _sorted(pics: List[Tuple[bytes, ImgRequest]]) -> List[Tuple[bytes, ImgRequest]]:
        def heading(bts_rq: Tuple[bytes, ImgRequest]):
            bts, rq = bts_rq
            return rq.fov

        return sorted(pics, key=heading)

    def _seams_handled(
        self, pics: List[Tuple[bytes, ImgRequest]]
    ) -> List[Tuple[bytes, ImgRequest]]:
        if self._dup_on_seams:
            return [pics[-1], *pics]
        return pics

    def _save(
        self, img: Image.Image, pics: List[Tuple[bytes, ImgRequest]]
    ) -> List[Path]:
        folder = self._dir / self._pano
        folder.mkdir(parents=True, exist_ok=True)
        name = "--".join(f"{rq.fov}-{rq.heading}" for _, rq in pics) + ".jpg"
        path = folder / name
        img.save(path)
        return [path]

import logging
from pathlib import Path
from typing import Callable, Tuple

import requests

from streetcrawl.pano import Pano
from streetcrawl.pano_folder import PanoFolder
from streetcrawl.pano_folder_simple import PanoFolderSimple


class Saver:
    def __init__(
        self,
        fov: int,
        resolution: Tuple[int, int],
        session: requests.Session,
        path: Path,
        pano_folder: Callable[[Path, str], PanoFolder] = PanoFolderSimple,
        logger: logging.Logger = logging.getLogger(__name__),
    ):
        self._folder: Callable[[Path, str], PanoFolder] = pano_folder
        self._session: requests.Session = session
        self._dir: Path = path
        self._fov: int = fov
        self._resolution: Tuple[int, int] = resolution
        self._logger: logging.Logger = logger

    def download(self, pano: Pano) -> bool:
        pano_folder = self._folder(self._dir, pano.id())
        images = []
        for rq in pano.image_requests(
            fov=self._fov, width=self._resolution[0], height=self._resolution[1]
        ):
            self._logger.info(f"Downloading {rq.url!r} ...")
            resp = self._session.get(rq.url)
            if resp.ok:
                images.append((resp.content, rq))
            else:
                self._logger.warning(
                    f"Got error downloading {rq.url!r} : {resp.status_code}."
                )
        pano_folder.save(images)
        return len(images) > 0

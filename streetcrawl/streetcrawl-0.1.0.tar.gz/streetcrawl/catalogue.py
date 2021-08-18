import csv
import logging
from abc import ABC, abstractmethod
from logging import Logger
from pathlib import Path
from typing import FrozenSet


from streetcrawl.pano import Pano
from streetcrawl.panos import Panos
from streetcrawl.saver import Saver


class Index(ABC):
    @abstractmethod
    def save(self, pano: Pano):
        pass


class IndexContinuable(Index):
    def __init__(
        self,
        directory: Path,
        saver: Saver,
    ):
        self._dir: Path = directory
        self._saver: Saver = saver
        self._writer = None
        self._saved = None

    def _index_path(self) -> Path:
        return self._dir / "index.csv"

    def _saved_panos(self) -> FrozenSet[str]:
        already_saved = set()
        if self._index_path().exists():
            with self._index_path().open() as f:
                for row in csv.reader(f):
                    pano_id, lat, lng = row
                    already_saved.add(pano_id.strip())
        return frozenset(already_saved)

    def __enter__(self):
        self._dir.mkdir(exist_ok=True)
        self._index = (
            self._index_path()
            .open("a" if self._index_path().exists() else "w")
            .__enter__()
        )
        self._writer = csv.writer(self._index)
        self._saved = self._saved_panos()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._index.__exit__(exc_type, exc_val, exc_tb)
        self._writer = None

    def save(self, pano: Pano):
        assert self._saved is not None
        if pano.id() not in self._saved and self._saver.download(pano):
            self._writer.writerow(
                [
                    pano.id(),
                    pano.location().latitude,
                    pano.location().longitude,
                ]
            )


class Catalogue:
    def __init__(
        self,
        idx: Index,
        logger: Logger = logging.getLogger(__name__),
    ):
        self._idx: Index = idx
        self._logger: Logger = logger

    def add(self, panos: Panos):
        panos_list = panos.as_list()
        self._logger.info(f"Got {len(panos_list)} panos to explore.")
        for i, pano in enumerate(panos_list, start=1):
            self._logger.info(f"Getting pano {i} of {len(panos_list)}...")
            self._idx.save(pano)

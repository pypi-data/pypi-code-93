import logging
import operator
from abc import ABC, abstractmethod
from logging import Logger
from typing import Callable, List, Iterable

from geopy import Point

from streetcrawl.pano import Pano
from streetcrawl.pano_id import PanoIdClosestTo


class Panos(ABC):
    @abstractmethod
    def as_list(self) -> List[Pano]:
        pass


class PanosSimple(Panos):
    def __init__(
        self,
        pts: Iterable[Point],
        pano_id: Callable[[Point], PanoIdClosestTo],
        pano: Callable[[str, Point], Pano],
        logger: Logger = logging.getLogger(__name__),
    ):
        self._pts: Iterable[Point] = pts
        self._pano_id: Callable[[Point], PanoIdClosestTo] = pano_id
        self._pano: Callable[[str, Point], Pano] = pano
        self._logger: Logger = logger

    def as_list(self) -> List[Pano]:
        ids = dict()
        for p in self._pts:
            self._logger.info(f"Getting pano id for {p.latitude},{p.longitude}...")
            pano_id = self._pano_id(p)
            id_str = pano_id.as_str()
            location = pano_id.pano_location()
            if id_str is not None:
                assert location is not None
                ids[id_str] = location
            else:
                self._logger.info(f"Got no pano id for {p.latitude},{p.longitude}.")
        return [
            self._pano(id_, location)
            for id_, location in sorted(ids.items(), key=operator.itemgetter(0))
        ]

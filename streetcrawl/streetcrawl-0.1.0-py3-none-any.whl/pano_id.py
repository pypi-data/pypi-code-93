from typing import Optional
from urllib.parse import quote

import requests
from geopy import Point
from methodtools import lru_cache


class PanoIdClosestTo:
    def __init__(self, coords: Point, api_key: str, session: requests.Session):
        self._key: str = api_key
        self._session: requests.Session = session
        self._coords: Point = coords

    def as_str(self) -> Optional[str]:
        data = self._resp()
        if data["status"] == "ZERO_RESULTS":
            return None
        if data["status"] == "OK":
            return data["pano_id"]
        return None

    def pano_location(self) -> Optional[Point]:
        data = self._resp()
        if data["status"] == "ZERO_RESULTS":
            return None
        if data["status"] == "OK":
            return Point(data["location"]["lat"], data["location"]["lng"])
        return None

    @lru_cache()
    def _resp(self):
        location = quote(f"{self._coords.latitude},{self._coords.longitude}")
        return self._session.get(
            f"https://maps.googleapis.com/maps/api/streetview/metadata?location={location}&key={self._key}"
        ).json()

    def location(self) -> Point:
        return self._coords

from typing import List, NamedTuple

from geopy import Point


class ImgRequest(NamedTuple):
    url: str
    fov: int
    heading: int


class Pano:
    def __init__(self, pano_id: str, location: Point, api_key: str):
        self._id: str = pano_id
        self._location: Point = location
        self._api_key: str = api_key

    def id(self) -> str:
        return self._id

    def location(self) -> Point:
        return self._location

    def image_requests(
        self, fov: int = 90, width: int = 900, height: int = 600
    ) -> List[ImgRequest]:
        assert 360 % 90 == 0
        return [
            ImgRequest(
                url=f"https://maps.googleapis.com/maps/api/streetview?size={width}x{height}"
                f"&pano={self._id}&heading={heading}&fov={fov}&key={self._api_key}&return_error_code=true",
                fov=fov,
                heading=heading,
            )
            for heading in range(0, 360, fov)
        ]

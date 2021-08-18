import geopy.distance
from geopy import Point


class PointsInSquare:
    def __init__(self, centre: Point, square_side: int = 1000, step: int = 20):
        self._centre: Point = centre
        self._side: int = square_side
        self._step: int = step

    def __iter__(self):
        start = self.upper_left_corner()
        for i in range(0, self._side + 1, 30):
            for j in range(0, self._side + 1, 30):
                yield geopy.distance.distance(meters=j).destination(
                    point=geopy.distance.distance(meters=i).destination(
                        point=start, bearing=90
                    ),
                    bearing=180,
                )

    def upper_left_corner(self) -> Point:
        left = geopy.distance.distance(meters=self._side / 2).destination(
            point=self._centre, bearing=270
        )
        upper_left = geopy.distance.distance(meters=self._side / 2).destination(
            point=left, bearing=0
        )
        return upper_left

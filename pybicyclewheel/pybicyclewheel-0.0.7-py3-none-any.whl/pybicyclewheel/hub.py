import math
import numpy as np


class Flange(object):
    def __init__(self, holes, diameter, distance, spoke_hole):
        self.holes = holes
        self.diameter = diameter  # pitch hole circle, not flange height
        self.distance = distance  # distance from the center
        self.spoke_hole = spoke_hole

        self.recalc()

    def __repr__(self):
        return str(self.__dict__)

    def recalc(self):
        self.radius = self.diameter / 2.0
        self.hole_alpha = 2 * math.pi / self.holes
        self.hole_alpha_deg = 360 / self.holes
        self.top_hole = np.array([0, self.radius, self.distance])

    def vec(self, cross=3):
        """this vector points from the center of the wheel to the hub hole"""

        self.recalc()

        alpha = cross * self.hole_alpha

        # rotation matrix for calc the right hole for the pointing vector
        # using the top_hole as reference for the rotation
        rot_z = np.array(
            [
                [np.cos(alpha), -np.sin(alpha), 0],
                [np.sin(alpha), np.cos(alpha), 0],
                [0, 0, 1],
            ]
        )

        # rotate the top hole to get the position
        # by multiply top_hole with rot_z matrix
        return self.top_hole @ rot_z


class Hub(object):
    def __init__(
        self,
        holes=36,
        diameter_l=61,
        diameter_r=61,
        distance_l=-35.35,
        distance_r=21.75,
        spoke_hole=2.8,
    ):
        self.holes = holes
        self.holes_per_side = self.holes / 2
        self.left = Flange(
            holes=self.holes_per_side,
            diameter=diameter_l,
            distance=distance_l,
            spoke_hole=spoke_hole,
        )
        self.right = Flange(
            holes=self.holes_per_side,
            diameter=diameter_r,
            distance=distance_r,
            spoke_hole=spoke_hole,
        )

    def __repr__(self):
        return str(self.__dict__)

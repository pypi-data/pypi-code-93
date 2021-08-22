import math
import numpy as np


class Rim(object):
    def __init__(self, erd=598, holes=36):
        self.erd = erd
        self.radius = erd / 2.0
        self.holes = holes
        self.hole_alpha = 2 * math.pi / self.holes
        self.hole_alpha_deg = 360 / self.holes

    def __repr__(self):
        return str(self.__dict__)

    def vec(self):
        """this vector points from the center of the wheel to the rim"""
        return np.array([0, self.radius, 0])

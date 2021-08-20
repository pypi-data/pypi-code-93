from math import radians
from typing import List

import healpy as hp
import numpy as np


def get_planck_scan(X_observer: np.ndarray, X_unit: np.ndarray, ) -> List[np.ndarray]:

    angular_distance = hp.rotator.angdist(X_observer , X_unit)
    
    min_angle = 85
    max_angle = 90
    observed_pixels = np.logical_and(
        angular_distance > radians(min_angle), 
        angular_distance < radians(max_angle)
    ) 

    return observed_pixels
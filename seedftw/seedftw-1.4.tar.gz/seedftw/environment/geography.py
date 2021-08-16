# -*- coding: utf-8 -*-
"""
Functions related to modelling of geography-related aspects.

This file can also be imported as a module and contains the following
functions:

    * distance_between_coordinates - computes distance between coordinates


References:
    [1] "Reference points and distance computations" (PDF), Code of Federal Regulations (Annual Edition). 
        Title 47: Telecommunication. 73 (208). October 1, 2016.
        URL: https://www.govinfo.gov/content/pkg/CFR-2016-title47-vol4/pdf/CFR-2016-title47-vol4-sec73-208.pdf

"""
import warnings
from typing import List

import numpy as np


# Sine and cosine in degrees
def cosd(x):
    return np.cos(x * (2 * np.pi / 360))


def sind(x):
    return np.sin(x * (2 * np.pi / 360))


def distance_between_coordinates(
    coordinates_1: List[float], coordinates_2: List[float]
) -> float:
    """Computes the distance between two sets of geographical coordinates

    Parameters
    ----------
    coordinates_1 : list(2)
        Coordinates in format [latitude,longitude] [degrees]
    coordinates_2 : list(2)
        Coordinates in format [latitude,longitude] [degrees]

    Raises
    ------
    None

    Returns
    -------
    distance : float
        Distance between the coordinates [km]
    """

    latitude_1 = coordinates_1[0]
    longitude_1 = coordinates_1[1]
    latitude_2 = coordinates_2[0]
    longitude_2 = coordinates_2[1]

    # With formulates from reference [1]
    latitude_M = (latitude_1 + latitude_2) / 2
    K1 = 111.13209 - 0.56605 * cosd(2 * latitude_M) + 0.00120 * cosd(4 * latitude_M)
    K2 = (
        111.41513 * cosd(latitude_M)
        - 0.09455 * cosd(3 * latitude_M)
        + 0.00012 * cosd(5 * latitude_M)
    )

    distance = np.sqrt(
        (K1 * (latitude_1 - latitude_2)) ** 2 + (K2 * (longitude_1 - longitude_2)) ** 2
    )

    if distance >= 475:
        warnings.warn(
            "WARNING: The distance estimation is not accurate at this distance ("
            + str()
            + " km > 475 km)"
        )
        distance = np.NAN

    return distance

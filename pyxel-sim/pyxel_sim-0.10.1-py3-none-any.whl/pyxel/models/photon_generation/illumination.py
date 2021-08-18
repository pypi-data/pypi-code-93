#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Pyxel photon generator models."""
import typing as t

import numpy as np

from pyxel.data_structure import Photon
from pyxel.detectors import Detector


# TODO: Fix this
# @validators.validate
# @config.argument(name='level', label='number of photon', units='', validate=check_type(int))
# @config.argument(name='option', label='type of illumination', units='',
#                  validate=check_choices(['uniform', 'rectangular_hole', 'elliptic_hole']))
# @config.argument(name='size', label='size of 2d array', units='', validate=check_type(list))
# @config.argument(name='hole_size', label='size of hole', units='', validate=check_type(list))
def illumination(
    detector: Detector,
    level: int,
    option: str = "uniform",
    array_size: t.Optional[t.Tuple[int, int]] = None,
    hole_size: t.Optional[t.Sequence[int]] = None,
    hole_center: t.Optional[t.Sequence[int]] = None,
) -> None:
    """Generate photon uniformly over the entire array or hole.

    detector: Detector
        Pyxel Detector object.
    level: int
        Number of photon per pixel.
    option: str{'uniform', 'elliptic_hole', 'rectangular_hole'}
        A string indicating the type of illumination:

        - ``uniform``
           Uniformly fill the entire array with photon. (Default)
        - ``elliptic_hole``
           Mask with elliptic hole.
        - ``rectangular_hole``
           Mask with rectangular hole.
    array_size: list, optional
        List of integers defining the size of 2d photon array.
    hole_size: list, optional
        List of integers defining the sizes of the elliptic or rectangular hole.
    hole_center: list, optional
        List of integers defining the center of the elliptic or rectangular hole.
    """
    if array_size is None:
        if not detector.has_photon:
            geo = detector.geometry
            detector.photon = Photon(np.zeros((geo.row, geo.col), dtype=int))

        num_rows, num_cols = detector.photon.array.shape
        shape = num_rows, num_cols  # type: t.Tuple[int, int]
    else:
        shape = array_size

    if option == "uniform":
        photon_array = np.ones(shape, dtype=int) * level

    elif option == "rectangular_hole":
        if hole_size:
            photon_array = np.zeros(shape, dtype=int)
            if hole_center is not None:
                if not (
                    (0 <= hole_center[0] <= shape[0])
                    and (0 <= hole_center[1] <= shape[1])
                ):
                    raise ValueError(
                        'Argument "hole_center" should be inside Photon array.'
                    )
            else:
                hole_center = [int(shape[0] / 2), int(shape[1] / 2)]
            p = hole_center[0] - int(hole_size[0] / 2)
            q = hole_center[1] - int(hole_size[1] / 2)
            p0 = int(np.clip(p, a_min=0, a_max=shape[0]))
            q0 = int(np.clip(q, a_min=0, a_max=shape[1]))
            photon_array[
                slice(p0, p + hole_size[0]), slice(q0, q + hole_size[1])
            ] = level
        else:
            raise ValueError(
                "hole_size argument should be defined for illumination model"
            )

    elif option == "elliptic_hole":
        if hole_size:
            photon_array = np.zeros(shape, dtype=int)
            if hole_center is not None:
                if not (
                    (0 <= hole_center[0] <= shape[0])
                    and (0 <= hole_center[1] <= shape[1])
                ):
                    raise ValueError(
                        'Argument "hole_center" should be inside Photon array.'
                    )
            else:
                hole_center = [int(shape[0] / 2), int(shape[1] / 2)]
            y, x = np.ogrid[: shape[0], : shape[1]]
            dist_from_center = np.sqrt(
                ((x - hole_center[1]) / hole_size[1]) ** 2
                + ((y - hole_center[0]) / hole_size[0]) ** 2
            )
            photon_array[dist_from_center < 1] = level
        else:
            raise ValueError(
                "hole_size argument should be defined for illumination model"
            )

    else:
        raise NotImplementedError

    try:
        detector.photon.array += photon_array
    except TypeError:
        detector.photon = Photon(photon_array)
    except ValueError:
        raise ValueError("Shapes of arrays do not match")

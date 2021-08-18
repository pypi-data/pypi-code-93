#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2021.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.
#
#
"""Stripe pattern illumination model."""

import typing as t

import numpy as np
import skimage.transform as tr

from pyxel.data_structure import Photon

if t.TYPE_CHECKING:
    from pyxel.detectors import Detector


def square_signal(n: int, lw: int, startwith: int = 0) -> list:
    """Compute a 1D periodic square signal.

    Parameters
    ----------
    n: int
        Length of the signal.
    lw:
        Width of a pulse.
    startwith
        1 to start with high level or 0 for 0.

    Returns
    -------
    out: list
        Output list.
    """
    if lw > n // 2:
        raise ValueError("Line too wide.")
    start = [startwith] * lw
    second = [1 - startwith] * lw
    pair = start + second
    num = n // len(pair)
    out = pair * num
    return out


def pattern(
    detector_shape: tuple,
    period: int = 2,
    level: float = 1,
    angle: float = 0,
    startwith: int = 0,
) -> np.ndarray:
    """Return an array of a periodic pattern.

    Parameters
    ----------
    detector_shape: tuple
        Detector shape.
    period: int
        Period of the periodic pattern in pixels.
    level: float
        Amplitude of the periodic pattern.
    angle: int
        Angle of the pattern in degrees.
    startwith: int
        1 to start with high level or 0 for 0.

    Returns
    -------
    out: np.ndarray
        Output stripe pattern.
    """

    if period < 2:
        raise ValueError("Cant set a period smaller than 2 pixels.")
    elif (period % 2) != 0:
        raise ValueError("Period should be a multiple of 2.")

    y, x = detector_shape

    n = max(y, x) * 2
    m = max(y, x) * 2

    sx = slice(n // 2 - y // 2, n // 2 + y // 2)
    sy = slice(m // 2 - x // 2, m // 2 + x // 2)

    signal = square_signal(n=n, lw=period // 2, startwith=startwith)
    signal = np.array(signal + ([1] * (n - len(signal))))[::-1]

    out = np.ones((n, m))

    for i in range(m):
        out[:, i] = signal

    out = level * out

    if angle:
        out = tr.rotate(out, angle=angle)

    out = out[sx, sy]

    return out


def stripe_pattern(
    detector: "Detector",
    period: int = 10,
    level: float = 1.0,
    angle: int = 0,
    startwith: int = 0,
) -> None:
    """Stripe pattern model.

    Parameters
    ----------
    detector: Detector
        Detector object.
    period: int
        Period of the periodic pattern in pixels.
    level: float
        Amplitude of the periodic pattern.
    angle: int
        Angle of the pattern in degrees.
    startwith: int
        1 to start with high level or 0 for 0.

    Returns
    -------
    None
    """

    photon_array = pattern(
        detector_shape=(detector.geometry.row, detector.geometry.col),
        period=period,
        level=level,
        startwith=startwith,
        angle=angle,
    )

    detector.photon = Photon(photon_array)

#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Fitness functions for model fitting."""

import typing as t

import numpy as np


def sum_of_abs_residuals(
    simulated: np.ndarray, target: np.ndarray, weighting: t.Optional[float] = None
) -> float:
    """TBW.

    Parameters
    ----------
    simulated
    target
    weighting

    Returns
    -------
    array
        TBW.
    """
    try:
        diff = target.astype(float) - simulated.astype(float)
    except AttributeError:
        diff = float(target) - float(simulated)

    if weighting is not None:
        diff *= weighting

    result = float(np.sum(np.abs(diff)))
    return result


def sum_of_squared_residuals(
    simulated: np.ndarray, target: np.ndarray, weighting: t.Optional[float] = None
) -> float:
    """TBW.

    Parameters
    ----------
    simulated
    target
    weighting

    Returns
    -------
    array
        TBW.
    """
    try:
        diff = target.astype(float) - simulated.astype(float)
    except AttributeError:
        diff = float(target) - float(simulated)
    diff_square = diff * diff

    if weighting is not None:
        diff_square *= weighting

    result = np.sum(diff_square)  # type: float
    return result

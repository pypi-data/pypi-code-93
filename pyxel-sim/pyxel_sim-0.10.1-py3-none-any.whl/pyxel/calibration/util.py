#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""TBW."""

import typing as t
from enum import Enum
from pathlib import Path

#  import attr
import numpy as np
import pandas as pd
import xarray as xr

#  from pyxel.pipelines import Processor

__all__ = [
    "CalibrationResult",
    "CalibrationMode",
    "Island",
    "ResultType",
    "check_ranges",
    "list_to_slice",
    "read_data",
]


# @attr.s(frozen=True, auto_attribs=True, slots=True)
# class CalibrationResult:
#     """TBW."""
#
#     processors: t.Sequence[Processor]
#     fitness: float
#     island: int
#     results: t.Mapping[str, t.Union[int, float]]


class CalibrationResult(t.NamedTuple):
    """Result class for calibration class."""

    dataset: xr.Dataset
    processors: pd.DataFrame
    logs: pd.DataFrame
    filenames: t.Sequence


class CalibrationMode(Enum):
    """TBW."""

    Pipeline = "pipeline"
    SingleModel = "single_model"


class ResultType(Enum):
    """TBW."""

    Image = "image"
    Signal = "signal"
    Pixel = "pixel"


class Island(Enum):
    """User defines num_islands provides by Pygmo."""

    MultiProcessing = "multiprocessing"
    MultiThreading = "multithreading"
    IPyParallel = "ipyparallel"


def read_single_data(filename: Path) -> np.ndarray:
    """Read a numpy array from a FITS or NPY file.

    Parameters
    ----------
    filename : Path

    Returns
    -------
    array
        TBW.
    """
    # Late import to avoid circular import
    from pyxel.inputs_outputs.loader import load_image

    data = load_image(filename)

    # # TODO: Is it the right manner ?
    # if data is None:
    #     raise OSError(f"Input file '{filename}' can not be read by Pyxel.")

    return data


def read_data(filenames: t.Sequence[Path]) -> t.Sequence[np.ndarray]:
    """Read numpy array(s) from several FITS or NPY files.

    :param filenames:
    :return:
    """
    output = [
        read_single_data(Path(filename)) for filename in filenames
    ]  # type: t.Sequence[np.ndarray]

    return output


# TODO: Create unit tests for this function
def list_to_slice(
    input_list: t.Optional[t.Sequence[int]] = None,
) -> t.Union[slice, t.Tuple[slice, slice]]:
    """TBW.

    :return:
    """
    if not input_list:
        return slice(None)

    if len(input_list) == 2:
        return slice(input_list[0], input_list[1])

    elif len(input_list) == 4:
        return slice(input_list[0], input_list[1]), slice(input_list[2], input_list[3])

    else:
        raise ValueError("Fitting range should have 2 or 4 values")


# TODO: Write unit tests for this function
def check_ranges(
    target_fit_range: t.Sequence[int],
    out_fit_range: t.Sequence[int],
    rows: int,
    cols: t.Optional[int] = None,
) -> None:
    """TBW."""
    if target_fit_range:
        if len(target_fit_range) not in (2, 4):
            raise ValueError

        if out_fit_range:
            if len(out_fit_range) not in (2, 4):
                raise ValueError

            if (target_fit_range[1] - target_fit_range[0]) != (
                out_fit_range[1] - out_fit_range[0]
            ):
                raise ValueError(
                    "Fitting ranges have different lengths in 1st dimension"
                )

            # TODO: It could be refactor in a more pythonic way
            if len(target_fit_range) == 4 and len(out_fit_range) == 4:
                if (target_fit_range[3] - target_fit_range[2]) != (
                    out_fit_range[3] - out_fit_range[2]
                ):
                    raise ValueError(
                        "Fitting ranges have different lengths in 2nd dimension"
                    )

        for i in [0, 1]:
            # TODO: It could be refactor in a more pythonic way
            if not (0 <= target_fit_range[i] <= rows):
                raise ValueError("Value of target fit range is wrong")

        if len(target_fit_range) == 4:
            if cols is None:
                raise ValueError("Target data is not a 2 dimensional array")

            for i in [2, 3]:
                # TODO: It could be refactor in a more pythonic way (this is optional)
                if not (0 <= target_fit_range[i] <= cols):
                    raise ValueError("Value of target fit range is wrong")

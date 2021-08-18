#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""TBW."""

# flake8: noqa
from .algorithm import AlgorithmType, Algorithm
from .user_defined import DaskBFE, DaskIsland
from .protocols import IslandProtocol, ProblemSingleObjective
from .util import (
    CalibrationResult,
    CalibrationMode,
    Island,
    ResultType,
    check_ranges,
    list_to_slice,
    read_data,
)
from .archipelago import MyArchipelago
from .calibration import Calibration, CalibrationMode


try:
    import pygmo

    del pygmo
except ImportError:
    import warnings

    warnings.warn("Cannot import 'pygmo", RuntimeWarning, stacklevel=2)

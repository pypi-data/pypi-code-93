import json
from typing import Union

import numpy as np
from astropy.time import Time

from dkist_processing_common.models.constants import BudName
from dkist_processing_common.models.flower_pot import SpilledDirt
from dkist_processing_common.parsers.l0_fits_access import L0FitsAccess
from dkist_processing_common.parsers.unique_bud import UniqueBud


class TimeBud(UniqueBud):
    """
    Base class for all Time Buds
    """

    def __init__(self, constant_name: str):
        super().__init__(constant_name, metadata_key="time_obs")

    def setter(self, fits_obj: L0FitsAccess) -> Union[float, SpilledDirt]:
        """
        If the file is an observe file, its DATE-OBS value is stored as unix seconds
        """
        if fits_obj.ip_task_type == "observe":
            return Time(getattr(fits_obj, self.metadata_key)).unix
        return SpilledDirt


class AverageCadenceBud(TimeBud):
    def __init__(self):
        super().__init__(constant_name=BudName.average_cadence.value)

    def getter(self, key) -> np.float64:
        """
        Return the mean cadence between frames
        """
        return np.mean(np.diff(sorted(list(self.key_to_petal_dict.values()))))


class MaximumCadenceBud(TimeBud):
    def __init__(self):
        super().__init__(constant_name=BudName.maximum_cadence.value)

    def getter(self, key) -> np.float64:
        """
        Return the maximum cadence between frames
        """
        return np.max(np.diff(sorted(list(self.key_to_petal_dict.values()))))


class MinimumCadenceBud(TimeBud):
    def __init__(self):
        super().__init__(constant_name=BudName.minimum_cadence.value)

    def getter(self, key) -> np.float64:
        """
        Return the minimum cadence between frames
        """
        return np.min(np.diff(sorted(list(self.key_to_petal_dict.values()))))


class VarianceCadenceBud(TimeBud):
    def __init__(self):
        super().__init__(constant_name=BudName.variance_cadence.value)

    def getter(self, key) -> np.float64:
        """
        Return the cadence variance between frames
        """
        return np.var(np.diff(sorted(list(self.key_to_petal_dict.values()))))


class TimeOrderBud(TimeBud):
    def __init__(self):
        super().__init__(constant_name=BudName.time_order.value)

    def getter(self, key) -> str:
        """
        Return the times as a json string that can be decoded to a list of floats
        """
        return json.dumps(sorted(list(self.key_to_petal_dict.values())))

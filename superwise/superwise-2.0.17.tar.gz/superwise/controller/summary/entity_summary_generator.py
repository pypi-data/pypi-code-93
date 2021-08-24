import collections.abc
import logging
from typing import Dict

import pandas as pd


logger = logging.getLogger(__name__)


class EntitySummaryGenerator:
    def __init__(self, entity: pd.Series):
        self._entity = entity

    @classmethod
    def _update(cls, summary, measurements):
        for k, v in measurements.items():
            if isinstance(v, collections.abc.Mapping):
                summary[k] = cls._update(summary.get(k, {}), v)
            else:
                summary[k] = v
        return summary

    def calc_missing_values(self):
        logger.debug(f"Calc missing values for {self._entity.name}")
        missing_values = float(self._entity.isna().sum() / len(self._entity))
        return {"statistics": {"missing_values": missing_values}}

    def generate_summary(self, secondary_type) -> Dict:
        logger.debug(f"Calc generic summary for {self._entity.name}")
        return self.calc_missing_values()

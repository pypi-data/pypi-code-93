import logging

import pandas as pd
from scipy.stats import entropy

from .entity_summary_generator import EntitySummaryGenerator
from superwise.resources.superwise_enums import CategoricalSecondaryType


logger = logging.getLogger(__name__)


class CategoricalSummaryGenerator(EntitySummaryGenerator):
    def calc_distribution(self):
        logger.debug(f"Calc distribution for {self._entity.name}")
        buckets = self._entity.value_counts(normalize=True).reset_index()
        buckets.columns = ["value", "frequency"]
        buckets = buckets.sort_values(["frequency", "value"])
        buckets = buckets.to_dict(orient="records")
        entropy = self.calc_entropy(buckets)
        return {"distribution": {"buckets": buckets}, "statistics": {"entropy": entropy}}

    def calc_entropy(self, buckets):
        freq = [b["frequency"] for b in buckets]
        entripy_val = entropy(freq)
        return entripy_val

    def calc_new_values(self):
        logger.debug(f"Calc new values for {self._entity.name}")
        return {"statistics": {"new_values": 0}}

    def calc_unique_values(self):
        logger.debug(f"Calc unique values for {self._entity.name}")
        unique_values = int(len(self._entity.unique()))
        return {"statistics": {"unique_values": unique_values}}

    def calc_top_frequent_percents(self):
        logger.debug(f"Calc top frequent percent for {self._entity.name}")
        top_frequent_percents = float(self._entity.value_counts(normalize=True).sort_values().iloc[-1])
        top_frequent_percents = None if pd.isna(top_frequent_percents) else top_frequent_percents
        return {"statistics": {"top_frequent_percents": top_frequent_percents}}

    def generate_summary(self, secondary_type: str):
        secondary_type_to_metrics = {
            CategoricalSecondaryType.SPARSE.value: [self.calc_missing_values],
            CategoricalSecondaryType.CONSTANT.value: [
                self.calc_missing_values,
                self.calc_new_values,
                self.calc_unique_values,
                self.calc_top_frequent_percents,
                self.calc_distribution,
            ],
            CategoricalSecondaryType.DENSE.value: [
                self.calc_missing_values,
                self.calc_new_values,
                self.calc_unique_values,
                self.calc_top_frequent_percents,
                self.calc_distribution,
            ],
        }

        logger.debug(f"Generate summary for categorical ({secondary_type}) feature {self._entity.name}")
        summary = {}
        for metric in secondary_type_to_metrics[secondary_type]:
            summary = self._update(summary, metric())
        return summary

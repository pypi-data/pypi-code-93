import logging

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

from .entity_summary_generator import EntitySummaryGenerator
from superwise.resources.superwise_enums import NumericSecondaryType

logger = logging.getLogger(__name__)


class NumericalSummaryGenerator(EntitySummaryGenerator):
    def __init__(self, entity):
        super(NumericalSummaryGenerator, self).__init__(entity)

    @classmethod
    def _head_tail_break_right(cls, data, breaks):
        n = len(data)
        m = data.mean()
        head = data[data > m]
        breaks.append(m)
        if len(head) < 0.4 * n:
            return cls._head_tail_break_right(head, breaks)
        else:
            return breaks

    @classmethod
    def _head_tail_break_left(cls, data, breaks):
        n = len(data)
        m = data.mean()
        tail = data[data < m]
        breaks.append(m)
        if len(tail) < 0.4 * n:
            return cls._head_tail_break_left(tail, breaks)
        else:
            return breaks

    def _long_tail_and_quantiles_bin(self, secondary_type):
        _, quantiles = pd.qcut(self._entity, 10, retbins=True, duplicates="drop")
        if secondary_type == NumericSecondaryType.NUM_RIGHT_TAIL.value:
            head_tail = np.array(self._head_tail_break_right(self._entity, breaks=[]))
            head_tail = head_tail[~pd.isna(head_tail)]
            head_tail.sort()
            return np.append(quantiles[quantiles < head_tail.min()], head_tail[1:])
        elif secondary_type == NumericSecondaryType.NUM_LEFT_TAIL.value:
            head_tail = np.array(self._head_tail_break_left(self._entity, breaks=[]))
            head_tail = head_tail[~pd.isna(head_tail)]
            head_tail.sort()
            return np.append(head_tail[:-1], quantiles[quantiles > head_tail.max()])
        else:
            return quantiles

    def _get_linear_percentile(self, quantile_deviation=0.03):
        # upper limit
        q_values = self._entity.astype(float).quantile(q=[0.98, 0.985, 0.99, 0.995])
        lr = LinearRegression().fit(q_values.reset_index()[["index"]], q_values.values)
        q_predict = 1 + quantile_deviation
        upper_limit = float(lr.predict(np.array(q_predict).reshape(-1, 1))[0])
        # Lower limit
        q_values = self._entity.astype(float).quantile(q=[0.005, 0.01, 0.015, 0.02])
        lr = LinearRegression().fit(q_values.reset_index()[["index"]], q_values.values)
        q_predict = 0 - quantile_deviation
        lower_limit = float(lr.predict(np.array(q_predict).reshape(-1, 1))[0])
        return lower_limit, upper_limit

    def calc_range(self):
        logger.debug("Calc range for".format(self._entity.name))
        lower_limit, upper_limit = self._get_linear_percentile()
        entities_count = self._entity.notna().sum()
        if entities_count:
            is_outlier_mask = (lower_limit > self._entity) | (self._entity > upper_limit)
            outliers_count = (is_outlier_mask & self._entity.notna()).sum()
            outliers = outliers_count / entities_count
        else:
            outliers = 0
        return {"range": {"from": lower_limit, "to": upper_limit}, "statistics": {"outliers": outliers}}

    def calc_min_value(self):
        logger.debug(f"Calc min value for {self._entity.name}")
        min_value = self._entity.min()
        min_value = None if pd.isna(min_value) else float(min_value)
        return {"statistics": {"min": min_value}}

    def calc_max_value(self):
        logger.debug(f"Calc max value for {self._entity.name}")
        max_value = self._entity.max()
        max_value = None if pd.isna(max_value) else float(max_value)
        return {"statistics": {"max": max_value}}

    def calc_std(self):
        logger.debug(f"Calc std value for {self._entity.name}")
        stdev = self._entity.std(ddof=1)
        logger.debug("calculated std {}".format(stdev))
        stdev = None if pd.isna(stdev) else float(stdev)
        return {"statistics": {"std": stdev}}

    def calc_mean_value(self):
        logger.debug(f"Calc mean value for {self._entity.name}")
        mean_value = self._entity.mean()
        mean_value = None if pd.isna(mean_value) else float(mean_value)
        return {"statistics": {"mean": mean_value}}

    def calc_distribution(self, secondary_type):
        return {
            NumericSecondaryType.NUM_RIGHT_TAIL.value: self.calc_right_tailed_distribution,
            NumericSecondaryType.NUM_LEFT_TAIL.value: self.calc_left_tailed_distribution,
            NumericSecondaryType.NUM_CENTERED.value: self.calc_centered_distribution,
        }[secondary_type]

    def calc_right_tailed_distribution(self):
        logger.debug(f"Calc right tail distribution for {self._entity.name}")
        bins = self._long_tail_and_quantiles_bin(NumericSecondaryType.NUM_RIGHT_TAIL.value)
        return self._calc_distribution(bins)

    def calc_left_tailed_distribution(self):
        logger.debug(f"Calc left tail distribution for {self._entity.name}")
        bins = self._long_tail_and_quantiles_bin(NumericSecondaryType.NUM_LEFT_TAIL.value)
        return self._calc_distribution(bins)

    def calc_centered_distribution(self):
        logger.debug(f"Calc centered distribution for {self._entity.name}")
        bins = self._long_tail_and_quantiles_bin(NumericSecondaryType.NUM_CENTERED.value)
        return self._calc_distribution(bins)

    def _calc_distribution(self, bins):
        bins = np.append(bins, [-np.Inf, np.Inf])
        bins.sort()
        buckets = pd.cut(self._entity, bins, right=False)
        buckets = buckets.value_counts(normalize=True, dropna=True).sort_index()
        buckets = pd.DataFrame(buckets).reset_index().reset_index().sort_values(by="index")
        buckets.columns = ["id", "name", "frequency"]
        buckets["lower"] = buckets["name"].values.categories.left
        buckets["upper"] = buckets["name"].values.categories.right

        mid_bin = list()
        bin_width = list()
        for idx, row in buckets.dropna().iterrows():
            if not {row["name"].right, row["name"].left}.intersection({np.Inf, -np.Inf}):
                mid_bin.append(row["name"].mid)
                bin_width.append(row["name"].length)

        if len(bin_width) == 0:
            bins_without_inf = bins[(bins < bins.max()) & (bins > bins.min())]
            mid_bin = [bins_without_inf[0] - 1, bins_without_inf[0] + 1]
            bin_width = [1, 1]
        else:
            bin_width.insert(0, bin_width[0])
            mid_bin.insert(0, buckets.iloc[0]["name"].right - bin_width[0] / 2)
            bin_width.append(bin_width[-1])
            mid_bin.append(buckets.dropna().iloc[-1]["name"].left + bin_width[-1] / 2)

        buckets["name"] = buckets["name"].astype(str)
        buckets["mid_bin"] = mid_bin
        buckets["bin_width"] = bin_width

        # remove -Inf & Inf
        bins = bins[1:-1]
        return {"distribution": {"bins": bins, "buckets": buckets.to_dict(orient="records")}}

    def generate_summary(self, secondary_type):
        secondary_type_to_metrics = {
            NumericSecondaryType.NUM_RIGHT_TAIL.value: [
                self.calc_missing_values,
                self.calc_range,
                self.calc_min_value,
                self.calc_max_value,
                self.calc_mean_value,
                self.calc_distribution(secondary_type),
                self.calc_std,
            ],
            NumericSecondaryType.NUM_LEFT_TAIL.value: [
                self.calc_missing_values,
                self.calc_range,
                self.calc_min_value,
                self.calc_max_value,
                self.calc_mean_value,
                self.calc_std,
                self.calc_distribution(secondary_type),
            ],
            NumericSecondaryType.NUM_CENTERED.value: [
                self.calc_missing_values,
                self.calc_range,
                self.calc_min_value,
                self.calc_max_value,
                self.calc_mean_value,
                self.calc_std,
                self.calc_distribution(secondary_type),
            ],
        }
        logger.debug(f"Generate summary for Numerical ({secondary_type}) feature {self._entity.name}")
        summary = {}
        for metric in secondary_type_to_metrics[secondary_type]:
            summary = self._update(summary, metric())
        return summary

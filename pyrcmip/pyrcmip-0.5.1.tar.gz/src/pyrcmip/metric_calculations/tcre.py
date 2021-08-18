"""
Calculation of the transient climate response (TCR)
"""
import logging

import scmdata

from .base import _CalculatorTCRTCREBase
from .utils import _add_index_level, _time_mean

LOGGER = logging.getLogger(__name__)


class CalculatorTCRE(_CalculatorTCRTCREBase):
    """
    Calculator of the transient climate response to emissions (TCRE)
    """

    @classmethod
    def _can_calculate_metric(cls, metric):
        return metric == "Transient Climate Response to Emissions"

    @classmethod
    def _calculate(
        cls, assessed_ranges, res_calc, norm_period, evaluation_period, unit
    ):
        res_calc_normed = cls._get_normed_res_calc(
            assessed_ranges, res_calc, norm_period, evaluation_period
        )

        common_filters = dict(scenario="1pctCO2", region="World",)
        gsat_var = "Surface Air Temperature Change"
        cumulative_emms_var = "Cumulative Emissions|CO2"
        temperatures = res_calc_normed.filter(variable=gsat_var, **common_filters)
        cumulative_emissions = res_calc_normed.filter(
            variable=cumulative_emms_var, **common_filters
        )

        tcre = []
        for temperatures_cm in temperatures.groupby("climate_model"):
            climate_model = temperatures_cm.get_unique_meta("climate_model", True)
            cumulative_emissions_cm = cumulative_emissions.filter(
                climate_model=climate_model, log_if_empty=False
            )
            if cumulative_emissions_cm.empty:
                LOGGER.warning(
                    "No {} for `{}`".format(cumulative_emms_var, climate_model)
                )
                continue

            tcre_cm = temperatures_cm.divide(
                cumulative_emissions_cm, op_cols={"variable": "TCRE"}
            )
            tcre.append(tcre_cm)

        tcre = scmdata.run_append(tcre)

        out = _time_mean(tcre.filter(year=range(1920, 1921)).convert_unit(unit))

        out = _add_index_level(
            out.reset_index("variable", drop=True),
            ",".join([gsat_var, cumulative_emms_var]),
            "variable",
        )

        return out

"""
Calculation of airborne fraction (of CO2)
"""
import logging

import numpy as np
import scmdata

from .base import Calculator
from .utils import _add_index_level, _time_mean

LOGGER = logging.getLogger(__name__)


class CalculatorAirborneFraction18501920(Calculator):
    """
    Calculator of the airborne fraction from 1850 to 1920
    """

    _start_year = 1850
    _end_year = 1920

    @classmethod
    def _can_calculate_metric(cls, metric):
        return metric == "Airborne Fraction|CO2 World 1pctCO2 1850-{}".format(
            cls._end_year
        )

    @classmethod
    def _calculate(
        cls, assessed_ranges, res_calc, norm_period, evaluation_period, unit
    ):
        cls._check_norm_period_evaluation_period(
            norm_period=norm_period,
            expected_norm_period=cls._start_year,
            evaluation_period=evaluation_period,
            expected_evaluation_period=cls._end_year,
        )

        common_filters = dict(
            scenario="1pctCO2",
            region="World",
            year=range(cls._start_year, cls._end_year + 1),
        )

        atmos_var = "Carbon Pool|Atmosphere"
        ocean_flux_var = "Net Atmosphere to Ocean Flux|CO2"
        land_flux_var = "Net Atmosphere to Land Flux|CO2"
        ocean_and_land_flux_var = "Net Atmosphere to Ocean and Land Flux|CO2"

        afs = []
        for res_calc_cm in res_calc.groupby("climate_model"):
            climate_model = res_calc_cm.get_unique_meta("climate_model", True)
            variables = res_calc_cm.get_unique_meta("variable")

            atmos_pool = res_calc_cm.filter(variable=atmos_var, **common_filters)
            if ocean_flux_var in variables and land_flux_var in variables:
                LOGGER.info(
                    "Using separate land and ocean fluxes for `{}`".format(
                        climate_model
                    )
                )
                ocean_fluxes = res_calc_cm.filter(
                    variable=ocean_flux_var, **common_filters
                )
                land_fluxes = res_calc_cm.filter(
                    variable=land_flux_var, **common_filters
                )

                assert not np.isnan(ocean_fluxes.values).any()
                assert not np.isnan(land_fluxes.values).any()

                ocean_and_land_flux = ocean_fluxes.add(
                    land_fluxes, op_cols={"variable": ocean_and_land_flux_var}
                )

            elif ocean_and_land_flux_var in variables:
                LOGGER.info(
                    "Using combined land and ocean fluxes for `{}`".format(
                        climate_model
                    )
                )
                ocean_and_land_flux = res_calc_cm.filter(
                    variable=ocean_and_land_flux_var, **common_filters
                )

                assert not np.isnan(ocean_and_land_flux.values).any()
            else:
                LOGGER.warning("No land or ocean fluxes for `{}`".format(climate_model))
                continue

            atmos_pool = assessed_ranges._get_normed_res_calc(atmos_pool, norm_period)

            ocean_and_land_pool = ocean_and_land_flux.integrate(
                "Carbon Pool|Ocean and Land"
            )
            ocean_and_land_pool = assessed_ranges._get_normed_res_calc(
                ocean_and_land_pool, norm_period
            )

            assert not np.isnan(atmos_pool.values).all()
            assert not np.isnan(ocean_and_land_pool.values).all()

            af = atmos_pool.divide(
                atmos_pool.add(
                    ocean_and_land_pool,
                    op_cols={"variable": "Atmos + Ocean + Land pool"},
                ),
                op_cols={"variable": "Airborne Fraction|CO2"},
            )
            afs.append(af)

        afs = scmdata.run_append(afs)
        out = _time_mean(
            afs.filter(year=range(cls._end_year, cls._end_year + 1)).convert_unit(unit)
        )

        out = _add_index_level(
            out.reset_index("variable", drop=True),
            ",".join([atmos_var, ocean_flux_var, land_flux_var]),
            "variable",
        )

        to_return = out.reset_index()
        to_return_idx = list(set(to_return.columns.tolist()) - {"value"})
        to_return = to_return.set_index(to_return_idx)["value"]

        return to_return


class CalculatorAirborneFraction18501990(CalculatorAirborneFraction18501920):
    """
    Calculator of the airborne fraction from 1850 to 1990
    """

    _start_year = 1850
    _end_year = 1990

from hestia_earth.schema import EmissionMethodTier, EmissionStatsDefinition

from hestia_earth.models.log import debugRequirements, logger
from hestia_earth.models.utils.emission import _new_emission
from hestia_earth.models.utils.input import get_inorganic_fertilizer_P_total
from hestia_earth.models.utils.measurement import most_relevant_measurement_value
from hestia_earth.models.utils.cycle import valid_site_type
from . import MODEL
from .utils import get_liquid_slurry_sludge_P_total

TERM_ID = 'pToSurfacewaterAllOrigins'


def _emission(value: float):
    logger.info('model=%s, term=%s, value=%s', MODEL, TERM_ID, value)
    emission = _new_emission(TERM_ID, MODEL)
    emission['value'] = [value]
    emission['methodTier'] = EmissionMethodTier.TIER_1.value
    emission['statsDefinition'] = EmissionStatsDefinition.MODELLED.value
    return emission


def _run(cycle: dict, slope: list, inorg_p_total: float, excreta_p_total: float):
    P_total = get_liquid_slurry_sludge_P_total(cycle)
    value_slope = 0 if slope < 3 else 1
    value_inorg_lss = 1 + inorg_p_total * 0.2/80 + P_total * 0.7/80
    value = value_slope * (value_inorg_lss + (P_total + excreta_p_total) * 0.4/80)
    return [_emission(value)]


def _should_run(cycle: dict):
    end_date = cycle.get('endDate')
    site = cycle.get('site', {})
    measurements = site.get('measurements', [])
    slope = most_relevant_measurement_value(measurements, 'slope', end_date)
    inorg_p_total = get_inorganic_fertilizer_P_total(cycle)
    # TODO: add excreta as input when is gone onto pasture
    excreta_p_total = 0

    debugRequirements(model=MODEL, term=TERM_ID,
                      slope=slope)

    should_run = all([valid_site_type(cycle, True), inorg_p_total, slope])
    logger.info('model=%s, term=%s, should_run=%s', MODEL, TERM_ID, should_run)
    return should_run, slope, inorg_p_total, excreta_p_total


def run(cycle: dict):
    should_run, slope, inorg_p_total, excreta_p_total = _should_run(cycle)
    return _run(cycle, slope, inorg_p_total, excreta_p_total) if should_run else []

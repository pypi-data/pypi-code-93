from hestia_earth.schema import EmissionMethodTier, EmissionStatsDefinition

from hestia_earth.models.log import logger
from hestia_earth.models.utils.cycle import get_excreta_N_total
from hestia_earth.models.utils.emission import _new_emission
from .noxToAirAllOrigins import _should_run, _get_value
from . import MODEL

TERM_ID = 'noxToAirExcreta'


def _emission(value: float):
    logger.info('model=%s, term=%s, value=%s', MODEL, TERM_ID, value)
    emission = _new_emission(TERM_ID, MODEL)
    emission['value'] = [value]
    emission['methodTier'] = EmissionMethodTier.TIER_2.value
    emission['statsDefinition'] = EmissionStatsDefinition.MODELLED.value
    return emission


def _run(cycle: dict, ecoClimateZone: str, nitrogenContent: float, N_total: float):
    noxToAirAllOrigins = _get_value(ecoClimateZone, nitrogenContent, N_total)
    excreta_N_total = get_excreta_N_total(cycle)
    return [_emission(excreta_N_total * noxToAirAllOrigins / N_total)]


def run(cycle: dict):
    should_run, ecoClimateZone, nitrogenContent, N_total, *args = _should_run(cycle)
    logger.info('model=%s, term=%s, should_run=%s', MODEL, TERM_ID, should_run)
    return _run(cycle, ecoClimateZone, nitrogenContent, N_total) if should_run else []

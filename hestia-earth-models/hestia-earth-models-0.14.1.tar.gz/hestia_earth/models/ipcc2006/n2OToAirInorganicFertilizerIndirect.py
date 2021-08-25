from hestia_earth.schema import EmissionMethodTier, EmissionStatsDefinition

from hestia_earth.models.log import debugRequirements, logger
from hestia_earth.models.utils.blank_node import find_terms_value
from hestia_earth.models.utils.input import get_inorganic_fertilizer_N_total
from hestia_earth.models.utils.emission import _new_emission
from hestia_earth.models.utils.cycle import valid_site_type
from .utils import get_nh3_nox, get_no3_value, COEFF_NH3NOX_N20
from . import MODEL

TERM_ID = 'n2OToAirInorganicFertilizerIndirect'
NO3_TERM_ID = 'no3ToGroundwaterInorganicFertilizer'
NH3_TERM_ID = 'nh3ToAirInorganicFertilizer'
NOX_TERM_ID = 'noxToAirInorganicFertilizer'


def _emission(value: float):
    logger.info('model=%s, term=%s, value=%s', MODEL, TERM_ID, value)
    emission = _new_emission(TERM_ID, MODEL)
    emission['value'] = [value]
    emission['methodTier'] = EmissionMethodTier.TIER_1.value
    emission['statsDefinition'] = EmissionStatsDefinition.MODELLED.value
    return emission


def _run(N_total: float, no3: float, nh3: float, nox: float):
    value = COEFF_NH3NOX_N20 * (N_total * 0.1 if nox == 0 or nh3 == 0 else nh3 + nox) + no3
    return [_emission(value)]


def _should_run(cycle: dict):
    N_total = get_inorganic_fertilizer_N_total(cycle)
    no3 = get_no3_value(find_terms_value(cycle.get('emissions', []), NO3_TERM_ID))
    nh3, nox = get_nh3_nox(cycle, NH3_TERM_ID, NOX_TERM_ID)

    debugRequirements(model=MODEL, term=TERM_ID,
                      N_total=N_total,
                      no3=no3,
                      nh3=nh3,
                      nox=nox)

    should_run = valid_site_type(cycle, True) and N_total > 0 and no3 > 0
    logger.info('model=%s, term=%s, should_run=%s', MODEL, TERM_ID, should_run)
    return should_run, N_total, no3, nh3, nox


def run(cycle: dict):
    should_run, N_total, no3, nh3, nox = _should_run(cycle)
    return _run(N_total, no3, nh3, nox) if should_run else []

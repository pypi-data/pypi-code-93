from hestia_earth.schema import EmissionMethodTier, EmissionStatsDefinition

from hestia_earth.models.log import debugRequirements, logger
from hestia_earth.models.utils.blank_node import find_terms_value
from hestia_earth.models.utils.emission import _new_emission
from hestia_earth.models.utils.cycle import valid_site_type
from .utils import get_nh3_nox, get_no3_value, COEFF_NH3NOX_N20
from . import MODEL

TERM_ID = 'n2OToAirCropResidueDecompositionIndirect'
NO3_TERM_ID = 'no3ToGroundwaterCropResidueDecomposition'
NH3_TERM_ID = 'nh3ToAirCropResidueDecomposition'
NOX_TERM_ID = 'noxToAirCropResidueDecomposition'


def _emission(value: float):
    logger.info('model=%s, term=%s, value=%s', MODEL, TERM_ID, value)
    emission = _new_emission(TERM_ID, MODEL)
    emission['value'] = [value]
    emission['methodTier'] = EmissionMethodTier.TIER_1.value
    emission['statsDefinition'] = EmissionStatsDefinition.MODELLED.value
    return emission


def _run(no3: float, nh3: float, nox: float):
    value = COEFF_NH3NOX_N20 * (nh3 + nox) + no3
    return [_emission(value)]


def _should_run(cycle: dict):
    no3 = get_no3_value(find_terms_value(cycle.get('emissions', []), NO3_TERM_ID))
    nh3, nox = get_nh3_nox(cycle, NH3_TERM_ID, NOX_TERM_ID)

    debugRequirements(model=MODEL, term=TERM_ID,
                      no3=no3,
                      nh3=nh3,
                      nox=nox)

    should_run = valid_site_type(cycle) and no3 > 0
    logger.info('model=%s, term=%s, should_run=%s', MODEL, TERM_ID, should_run)
    return should_run, no3, nh3, nox


def run(cycle: dict):
    should_run, no3, nh3, nox = _should_run(cycle)
    return _run(no3, nh3, nox) if should_run else []

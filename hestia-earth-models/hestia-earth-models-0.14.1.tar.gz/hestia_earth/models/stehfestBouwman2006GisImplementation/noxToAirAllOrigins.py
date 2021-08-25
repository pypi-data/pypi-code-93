from hestia_earth.schema import EmissionMethodTier, EmissionStatsDefinition
from hestia_earth.utils.lookup import download_lookup, get_table_value
from hestia_earth.utils.tools import list_sum, safe_parse_float

from hestia_earth.models.log import debugRequirements, logger
from hestia_earth.models.utils.emission import _new_emission
from hestia_earth.models.utils.input import get_total_nitrogen
from hestia_earth.models.utils.product import residue_nitrogen
from hestia_earth.models.utils.cycle import valid_site_type
from . import MODEL

TERM_ID = 'noxToAirAllOrigins'


def _should_run(cycle: dict):
    country_id = cycle.get('site', {}).get('country', {}).get('@id')
    residue = residue_nitrogen(cycle.get('products', []))
    N_total = list_sum(get_total_nitrogen(cycle.get('inputs', [])) + [residue])

    debugRequirements(model=MODEL, term=TERM_ID,
                      country_id=country_id,
                      residue=residue,
                      N_total=N_total)

    should_run = valid_site_type(cycle) and country_id is not None and N_total > 0
    return should_run, country_id, N_total, residue


def _get_value(country_id: str, N_total: float):
    lookup = download_lookup('region.csv', True)
    value = safe_parse_float(get_table_value(lookup, 'termid', country_id, 'ef_nox'))
    value = value * N_total
    logger.info('model=%s, term=%s, value=%s', MODEL, TERM_ID, value)
    return value


def _emission(value: float):
    logger.info('model=%s, term=%s, value=%s', MODEL, TERM_ID, value)
    emission = _new_emission(TERM_ID, MODEL)
    emission['value'] = [value]
    emission['methodTier'] = EmissionMethodTier.TIER_1.value
    emission['statsDefinition'] = EmissionStatsDefinition.MODELLED.value
    return emission


def _run(country_id: str, N_total: float):
    value = _get_value(country_id, N_total)
    return [_emission(value)]


def run(cycle: dict):
    should_run, country_id, N_total, *args = _should_run(cycle)
    logger.info('model=%s, term=%s, should_run=%s', MODEL, TERM_ID, should_run)
    return _run(country_id, N_total) if should_run else []

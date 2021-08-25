from hestia_earth.schema import PracticeStatsDefinition
from hestia_earth.utils.lookup import download_lookup, get_table_value, column_name
from hestia_earth.utils.tools import safe_parse_float

from hestia_earth.models.log import debugRequirements, logger
from hestia_earth.models.utils.practice import _new_practice
from . import MODEL

TERM_ID = 'croppingDuration'
LOOKUP_TABLE = 'region-ch4ef-IPCC2019.csv'
LOOKUP_COL_PREFIX = 'Rice_croppingDuration_days'


def _practice(value: float, min: float, max: float, sd: float):
    logger.info('model=%s, term=%s, value=%s', MODEL, TERM_ID, value)
    practice = _new_practice(TERM_ID, MODEL)
    practice['value'] = [value]
    practice['min'] = [min]
    practice['max'] = [max]
    practice['sd'] = [sd]
    practice['statsDefinition'] = PracticeStatsDefinition.MODELLED.value
    return practice


def _get_value(country: str, col: str):
    lookup = download_lookup(LOOKUP_TABLE, True)
    return safe_parse_float(get_table_value(lookup, 'termid', country, column_name(col)))


def _run(country: str, cycleDuration: float):
    value = _get_value(country, LOOKUP_COL_PREFIX)
    min = _get_value(country, f"{LOOKUP_COL_PREFIX}_min")
    max = _get_value(country, f"{LOOKUP_COL_PREFIX}_max")
    sd = _get_value(country, f"{LOOKUP_COL_PREFIX}_sd")
    return [_practice(value, min, max, sd)] if value <= cycleDuration else []


def _should_run(cycle: dict):
    country = cycle.get('site', {}).get('country', {}).get('@id')
    cycleDuration = cycle.get('cycleDuration', 0)

    debugRequirements(model=MODEL, term=TERM_ID,
                      country=country,
                      cycleDuration=cycleDuration)

    should_run = country is not None and cycleDuration > 0
    logger.info('model=%s, term=%s, should_run=%s', MODEL, TERM_ID, should_run)
    return should_run, country, cycleDuration


def run(cycle: dict):
    should_run, country, cycleDuration = _should_run(cycle)
    return _run(country, cycleDuration) if should_run else []

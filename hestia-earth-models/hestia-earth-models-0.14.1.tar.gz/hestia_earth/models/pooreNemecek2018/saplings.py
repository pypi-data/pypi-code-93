from hestia_earth.schema import InputStatsDefinition
from hestia_earth.utils.lookup import get_table_value, download_lookup
from hestia_earth.utils.tools import non_empty_list, safe_parse_float

from hestia_earth.models.log import logger
from hestia_earth.models.utils.input import _new_input
from hestia_earth.models.utils.dataCompleteness import _is_term_type_incomplete
from hestia_earth.models.utils.cycle import valid_site_type
from . import MODEL

TERM_ID = 'saplings'


def _get_value(product: dict):
    lookup = download_lookup('crop.csv', True)
    term_id = product.get('term', {}).get('@id', '')

    in_lookup = term_id in list(lookup.termid)
    logger.debug('Found lookup data for Term: %s? %s', term_id, in_lookup)

    return safe_parse_float(get_table_value(lookup, 'termid', term_id, 'saplings'), None) if in_lookup else None


def _input(value: float):
    logger.info('model=%s, term=%s, value=%s', MODEL, TERM_ID, value)
    input = _new_input(TERM_ID, MODEL)
    input['value'] = [value]
    input['statsDefinition'] = InputStatsDefinition.MODELLED.value
    return input


def _run(cycle: dict):
    def run_product(product):
        value = _get_value(product)
        return None if value is None else _input(value)

    return non_empty_list(map(run_product, cycle.get('products', [])))


def _should_run(cycle: dict):
    should_run = valid_site_type(cycle, True) and _is_term_type_incomplete(cycle, TERM_ID)
    logger.info('model=%s, term=%s, should_run=%s', MODEL, TERM_ID, should_run)
    return should_run


def run(cycle: dict): return _run(cycle) if _should_run(cycle) else []

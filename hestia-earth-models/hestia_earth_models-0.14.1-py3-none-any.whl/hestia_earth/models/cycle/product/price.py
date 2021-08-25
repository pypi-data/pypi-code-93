from hestia_earth.utils.lookup import get_table_value, column_name, download_lookup, extract_grouped_data
from hestia_earth.utils.tools import non_empty_list, safe_parse_float

from hestia_earth.models.log import logger
from hestia_earth.models.utils.product import _new_product
from .. import MODEL

MODEL_KEY = 'price'


def _product(term: dict, value: float):
    # divide by 1000 to convert price per tonne to kg
    value = value / 1000
    logger.info('model=%s, key=%s, value=%s, term=%s', MODEL, MODEL_KEY, value, term.get('@id'))
    product = _new_product(term)
    product[MODEL_KEY] = value
    return product


def _run(cycle: dict, product: dict):
    crop_lookup = download_lookup('crop.csv', True)

    # get the grouping used in region lookup
    term_id = product.get('term', {}).get('@id', '')
    grouping = get_table_value(crop_lookup, 'termid', term_id, column_name('cropGroupingFAOSTAT'))

    # based on annual value averaged between 1991-2018, source: FAOSTAT
    lookup = download_lookup('region-crop-cropGroupingFAOSTAT-price.csv')
    country_id = cycle.get('site', {}).get('country', {}).get('@id')
    logger.debug('Price data for term=%s, country=%s, grouping=%s', term_id, country_id, grouping)
    price_data = get_table_value(lookup, 'termid', country_id, column_name(grouping)) if grouping else None
    avg_price = extract_grouped_data(price_data, 'Average_price_per_tonne')
    value = safe_parse_float(avg_price, None)
    return None if value is None else _product(product.get('term', {}), value)


def _should_run_product(product: dict):
    term_id = product.get('term', {}).get('@id')
    should_run = MODEL_KEY not in product.keys() and len(product.get('value', [])) > 0
    logger.info('model=%s, key=%s, should_run=%s, term=%s', MODEL, MODEL_KEY, should_run, term_id)
    return should_run


def _should_run(cycle: dict):
    country_id = cycle.get('site', {}).get('country', {}).get('@id')
    should_run = country_id is not None
    logger.info('model=%s, key=%s, should_run=%s', MODEL, MODEL_KEY, should_run)
    return should_run


def run(cycle: dict):
    should_run = _should_run(cycle)
    products = list(filter(_should_run_product, cycle.get('products', []))) if should_run else []
    return non_empty_list(map(lambda p: _run(cycle, p), products))

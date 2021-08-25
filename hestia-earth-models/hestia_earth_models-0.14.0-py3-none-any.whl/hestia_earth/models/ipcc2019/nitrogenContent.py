from hestia_earth.schema import PropertyStatsDefinition
from hestia_earth.utils.model import find_primary_product, find_term_match
from hestia_earth.utils.lookup import get_table_value, download_lookup, column_name
from hestia_earth.utils.tools import non_empty_list, safe_parse_float

from hestia_earth.models.log import debugRequirements, logger
from hestia_earth.models.utils.property import _new_property
from . import MODEL

TERM_ID = 'nitrogenContent'
PRODUCT_COLUMN_MAPPING = {
    'aboveGroundCropResidueTotal': 'N_Content_AG_Residue',
    'belowGroundCropResidue': 'N_Content_BG_Residue'
}


def _property(value: float, product_term_id: str):
    logger.info('term=%s, product=%s, value=%s', TERM_ID, product_term_id, value)
    prop = _new_property(TERM_ID, MODEL)
    prop['value'] = value
    prop['statsDefinition'] = PropertyStatsDefinition.MODELLED.value
    return prop


def _get_value(crop_id: str, term: dict):
    lookup = download_lookup('crop.csv', True)
    term_id = term.get('@id', '')

    in_lookup = crop_id in list(lookup.termid)
    logger.debug('Found lookup data for Term: %s? %s', crop_id, in_lookup)

    if crop_id in list(lookup.termid):
        column = column_name(PRODUCT_COLUMN_MAPPING[term_id])
        value = safe_parse_float(get_table_value(lookup, 'termid', crop_id, column), 0)
        return value if value > 0 else None
    return None


def _should_run_product(product: dict):
    product_term_id = product.get('term', {}).get('@id')
    should_run = product_term_id in PRODUCT_COLUMN_MAPPING \
        and find_term_match(product.get('properties', []), TERM_ID, None) is None
    logger.info('model=%s, term=%s, should_run=%s', MODEL, product_term_id, should_run)
    return should_run


def _run(primary_product: dict, products: list):
    product_id = primary_product.get('term', {}).get('@id')

    def run_product(product: dict):
        product_term = product.get('term', {})
        value = _get_value(product_id, product_term)
        prop = _property(value, product_term.get('@id')) if value is not None else None
        return {**product, 'properties': product.get('properties', []) + [prop]} if prop else product

    return non_empty_list(map(run_product, products))


def _should_run(cycle: dict):
    product = find_primary_product(cycle)
    products = list(filter(_should_run_product, cycle.get('products', [])))

    debugRequirements(model=MODEL, term=TERM_ID, products=len(products))

    should_run = product is not None and len(products) > 0
    logger.info('model=%s, term=%s, should_run=%s', MODEL, TERM_ID, should_run)
    return should_run, product, products


def run(cycle: dict):
    should_run, product, products = _should_run(cycle)
    return _run(product, products) if should_run else []

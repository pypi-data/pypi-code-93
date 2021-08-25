from hestia_earth.utils.tools import non_empty_list

from hestia_earth.models.log import logger
from hestia_earth.models.utils.product import _new_product
from .. import MODEL

MODEL_KEY = 'revenue'


def _run(product: dict):
    value = product.get('value', [1])[0] * product.get('price', 0)
    logger.info('model=%s, key=%s, value=%s, term=%s', MODEL, MODEL_KEY, value, product.get('term', {}).get('@id'))
    product = _new_product(product.get('term', {}))
    product[MODEL_KEY] = value
    return product


def _should_run(product: dict):
    term_id = product.get('term', {}).get('@id')
    should_run = MODEL_KEY not in product.keys() and len(product.get('value', [])) > 0 and product.get('price', 0) > 0
    logger.info('model=%s, key=%s, should_run=%s, term=%s', MODEL, MODEL_KEY, should_run, term_id)
    return should_run


def run(cycle: dict):
    products = list(filter(_should_run, cycle.get('products', [])))
    return non_empty_list(map(_run, products))

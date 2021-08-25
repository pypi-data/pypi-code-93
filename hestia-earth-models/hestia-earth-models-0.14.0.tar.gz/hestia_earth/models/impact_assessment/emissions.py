from hestia_earth.schema import IndicatorStatsDefinition
from hestia_earth.utils.tools import list_sum

from hestia_earth.models.log import logger
from hestia_earth.models.utils.impact_assessment import get_product
from hestia_earth.models.utils.indicator import _new_indicator
from . import MODEL


def _indicator(term: str, value: float):
    logger.info('term=%s, value=%s', term.get('@id'), value)
    indicator = _new_indicator(term)
    indicator['value'] = value
    indicator['statsDefinition'] = IndicatorStatsDefinition.MODELLED.value
    return indicator


def _run_emission(product_value: float, economic_value: float):
    def run(emission: dict):
        emission_value = list_sum(emission.get('value', [0]))
        value = emission_value / product_value * (economic_value / 100)
        return _indicator(emission.get('term', {}), value)
    return run


def _should_run(impact_assessment: dict):
    product = get_product(impact_assessment)
    product_value = list_sum(product.get('value', [0])) if product else 0
    economic_value = product.get('economicValueShare') if product else None
    should_run = economic_value is not None and product_value > 0
    logger.info('model=%s, should_run=%s', MODEL, should_run)
    return should_run, product_value, economic_value


def run(impact_assessment: dict):
    should_run, product_value, economic_value = _should_run(impact_assessment)
    emissions = impact_assessment.get('cycle', {}).get('emissions', [])
    return list(map(_run_emission(product_value, economic_value), emissions)) if should_run else []

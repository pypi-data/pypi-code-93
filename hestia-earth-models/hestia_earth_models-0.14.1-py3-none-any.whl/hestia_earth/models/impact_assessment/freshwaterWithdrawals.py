from hestia_earth.schema import IndicatorStatsDefinition, TermTermType
from hestia_earth.utils.tools import list_sum
from hestia_earth.utils.model import filter_list_term_type

from hestia_earth.models.log import debugRequirements, logger
from hestia_earth.models.utils.indicator import _new_indicator
from hestia_earth.models.utils.impact_assessment import get_product
from hestia_earth.models.utils.blank_node import get_total_value
from . import MODEL

TERM_ID = 'freshwaterWithdrawals'


def _indicator(value: float):
    logger.info('model=%s, term=%s, value=%s', MODEL, TERM_ID, value)
    indicator = _new_indicator(TERM_ID)
    indicator['value'] = value
    indicator['statsDefinition'] = IndicatorStatsDefinition.MODELLED.value
    return indicator


def _run(irrigation: float, pyield: float, economic_value: float):
    value = (irrigation / pyield) * economic_value / 100
    return [_indicator(value)]


def _should_run(impact_assessment: dict):
    inputs = impact_assessment.get('cycle', {}).get('inputs', [])

    filter_irrigation = filter_list_term_type(inputs, TermTermType.WATER)
    irrigation = list_sum(get_total_value(filter_irrigation))

    product = get_product(impact_assessment)
    pyield = list_sum(product.get('value', [])) if product else 0
    economic_value = product.get('economicValueShare', 0) if product else 0

    debugRequirements(model=MODEL, term=TERM_ID,
                      irrigation=irrigation,
                      product_yield=pyield,
                      economic_value=economic_value)

    should_run = irrigation > 0 \
        and pyield > 0 \
        and economic_value > 0
    logger.info('model=%s, term=%s, should_run=%s', MODEL, TERM_ID, should_run)
    return should_run, irrigation, pyield, economic_value


def run(impact_assessment: dict):
    should_run, irrigation, pyield, economic_value = _should_run(impact_assessment)
    return _run(irrigation, pyield, economic_value) if should_run else []

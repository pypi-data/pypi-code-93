from hestia_earth.schema import IndicatorStatsDefinition
from hestia_earth.utils.tools import safe_parse_float
from hestia_earth.utils.model import find_term_match

from hestia_earth.models.log import debugRequirements, logger
from hestia_earth.models.utils.indicator import _new_indicator
from hestia_earth.models.utils.impact_assessment import get_site
from .utils import get_region_factor
from . import MODEL

TERM_ID = 'biodiversityLossLandOccupation'


def _indicator(value: float):
    logger.info('model=%s, term=%s, value=%s', MODEL, TERM_ID, value)
    indicator = _new_indicator(TERM_ID, MODEL)
    indicator['value'] = value
    indicator['statsDefinition'] = IndicatorStatsDefinition.MODELLED.value
    return indicator


def _run(occupation_value: float, occupation_factor: float):
    value = occupation_value * occupation_factor
    return _indicator(value)


def _should_run(impact_assessment: dict):
    emissionsResourceUse = impact_assessment.get('emissionsResourceUse', [])
    occupation_value = safe_parse_float(find_term_match(emissionsResourceUse, 'landOccupation').get('value'))

    product = impact_assessment.get('product')
    country = impact_assessment.get('country', {}).get('@id')
    ecoregion = get_site(impact_assessment).get('ecoregion')
    occupation_factor = get_region_factor(product, country, ecoregion, 'occupation')

    debugRequirements(model=MODEL, term=TERM_ID,
                      occupation_value=occupation_value,
                      occupation_factor=occupation_factor)

    should_run = occupation_value is not None and occupation_factor is not None
    logger.info('model=%s, term=%s, should_run=%s', MODEL, TERM_ID, should_run)
    return should_run, occupation_value, occupation_factor


def run(impact_assessment: dict):
    should_run, occupation_value, occupation_factor = _should_run(impact_assessment)
    return _run(occupation_value, occupation_factor) if should_run else None

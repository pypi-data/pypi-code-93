from hestia_earth.schema import IndicatorStatsDefinition
from hestia_earth.utils.tools import list_sum, safe_parse_float
from hestia_earth.utils.model import find_term_match

from hestia_earth.models.log import debugRequirements, logger
from hestia_earth.models.utils.indicator import _new_indicator
from hestia_earth.models.utils.impact_assessment import get_site
from .utils import get_region_factor
from . import MODEL

TERM_ID = 'biodiversityLossLandTransformation'
TRANSFORMATION_TERM_IDS = [
    'landTransformationFromForest20YearAverage',
    'landTransformationFromOtherNaturalVegetation20YearAverage'
]


def _indicator(value: float):
    logger.info('model=%s, term=%s, value=%s', MODEL, TERM_ID, value)
    indicator = _new_indicator(TERM_ID, MODEL)
    indicator['value'] = value
    indicator['statsDefinition'] = IndicatorStatsDefinition.MODELLED.value
    return indicator


def _run(transformation_value: float, transformation_factor: float):
    value = transformation_value * transformation_factor
    return _indicator(value)


def _should_run(impact_assessment: dict):
    def emission_value(term_id: str):
        value = find_term_match(impact_assessment.get('emissionsResourceUse', []), term_id).get('value')
        return safe_parse_float(value) if value else None

    transformation_value = list_sum([
        emission_value(term_id) for term_id in TRANSFORMATION_TERM_IDS if emission_value(term_id)
    ], None)

    product = impact_assessment.get('product')
    country = impact_assessment.get('country', {}).get('@id')
    ecoregion = get_site(impact_assessment).get('ecoregion')
    transformation_factor = get_region_factor(product, country, ecoregion, 'transformation')

    debugRequirements(model=MODEL, term=TERM_ID,
                      transformation_value=transformation_value,
                      transformation_factor=transformation_factor)

    should_run = transformation_value is not None and transformation_factor is not None
    logger.info('model=%s, term=%s, should_run=%s', MODEL, TERM_ID, should_run)
    return should_run, transformation_value, transformation_factor


def run(impact_assessment: dict):
    should_run, transformation_value, transformation_factor = _should_run(impact_assessment)
    return _run(transformation_value, transformation_factor) if should_run else None

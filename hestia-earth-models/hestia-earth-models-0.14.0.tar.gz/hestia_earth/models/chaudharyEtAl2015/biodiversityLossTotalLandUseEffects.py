from hestia_earth.schema import IndicatorStatsDefinition
from hestia_earth.utils.tools import list_sum, safe_parse_float
from hestia_earth.utils.model import find_term_match

from hestia_earth.models.log import debugRequirements, logger
from hestia_earth.models.utils.indicator import _new_indicator
from .biodiversityLossLandOccupation import TERM_ID as TERM_ID_1
from .biodiversityLossLandTransformation import TERM_ID as TERM_ID_2
from . import MODEL

TERM_ID = 'biodiversityLossTotalLandUseEffects'
BIODIVERSITY_TERM_IDS = [TERM_ID_1, TERM_ID_2]


def _indicator(value: float):
    logger.info('model=%s, term=%s, value=%s', MODEL, TERM_ID, value)
    indicator = _new_indicator(TERM_ID, MODEL)
    indicator['value'] = value
    indicator['statsDefinition'] = IndicatorStatsDefinition.MODELLED.value
    return indicator


def _should_run(impact_assessment: dict):
    def impact_value(term_id: str):
        value = find_term_match(impact_assessment.get('impacts', []), term_id).get('value')
        return safe_parse_float(value) if value else None

    values = [impact_value(term_id) for term_id in BIODIVERSITY_TERM_IDS if impact_value(term_id)]

    debugRequirements(model=MODEL, term=TERM_ID,
                      values=len(values))

    should_run = len(values) == len(BIODIVERSITY_TERM_IDS)
    logger.info('model=%s, term=%s, should_run=%s', MODEL, TERM_ID, should_run)
    return should_run, list_sum(values)


def run(impact_assessment: dict):
    should_run, value = _should_run(impact_assessment)
    return _indicator(value) if should_run else None

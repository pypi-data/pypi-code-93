from enum import Enum
from hestia_earth.utils.lookup import download_lookup, get_table_value
from hestia_earth.utils.tools import safe_parse_float

from hestia_earth.models.log import logger


class PRODUCTIVITY(Enum):
    HIGH = 'high'
    LOW = 'low'


HIGH_VALUE = 0.8
PRODUCTIVITY_KEY = {
    PRODUCTIVITY.HIGH: lambda hdi: hdi > HIGH_VALUE,
    PRODUCTIVITY.LOW: lambda hdi: hdi <= HIGH_VALUE
}


def _get_productivity(country_id: str, default: PRODUCTIVITY = PRODUCTIVITY.HIGH):
    lookup = download_lookup('region.csv', True)
    in_lookup = country_id in list(lookup.termid)
    logger.debug('Found productivity data for country: %s? %s', country_id, in_lookup)
    hdi = safe_parse_float(get_table_value(lookup, 'termid', country_id, 'hdi'), None) if in_lookup else None
    return next((key for key in PRODUCTIVITY_KEY if hdi and PRODUCTIVITY_KEY[key](hdi)), default)

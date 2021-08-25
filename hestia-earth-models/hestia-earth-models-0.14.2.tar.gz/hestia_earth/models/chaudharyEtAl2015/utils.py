from hestia_earth.utils.lookup import download_lookup, get_table_value, column_name
from hestia_earth.utils.tools import safe_parse_float

from hestia_earth.models.log import logger


def get_region_factor(product: dict, country: str, ecoregion: str, factor: str):
    try:
        lookup_name = 'ecoregion' if ecoregion else 'region' if country else None
        col = 'ecoregion' if ecoregion else 'termid' if country else None
        grouping = get_table_value(
            download_lookup(f"{product.get('termType')}.csv", True), 'termid', product.get('@id'),
            column_name('cropGroupingFAO'))
        logger.debug('factor=%s for product=%s with grouping=%s', factor, product.get('@id'), grouping)
        return safe_parse_float(
            get_table_value(download_lookup(f"{lookup_name}.csv", True), col, ecoregion or country,
                            column_name(f"{grouping}_TAXA_AGGREGATED_Median_{factor}"))
        ) if grouping and lookup_name else None
    except Exception:
        return None

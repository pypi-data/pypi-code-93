from functools import reduce
from hestia_earth.utils.model import find_term_match
from hestia_earth.utils.lookup import download_lookup, get_table_value, column_name
from hestia_earth.utils.tools import list_sum, safe_parse_float, non_empty_list

from hestia_earth.models.log import logger
from hestia_earth.models.data.impact_assessments import load_impacts


def _get_impacts_dict():
    def merge_impact(prev: dict, impact: dict):
        key = impact.get('product', {}).get('@id')
        return {**prev, key: impact}

    impacts = load_impacts()
    return reduce(merge_impact, impacts, {})


def get_product(impact_assessment: dict) -> dict:
    """
    Get the full `Product` from the `ImpactAssessment.cycle`.

    Parameters
    ----------
    impact_assessment : dict
        The `ImpactAssessment`.

    Returns
    -------
    dict
        The `Product` of the `ImpactAssessment`.
    """
    product = impact_assessment.get('product', {})
    products = impact_assessment.get('cycle', {}).get('products', [])
    return find_term_match(products, product.get('@id'), None)


def get_site(impact_assessment: dict) -> dict:
    return impact_assessment.get('site', impact_assessment.get('cycle', {}).get('site', {}))


def _emission_value(lookup, lookup_col: str):
    def get_value(emission: dict):
        term_id = emission.get('term', {}).get('@id')
        # TODO: remove replace - when fixed in utils
        data = get_table_value(lookup, 'termid', term_id, column_name(lookup_col).replace('-', ''))
        value = emission.get('value', 0)
        coefficient = safe_parse_float(data)
        logger.debug('term=%s, value=%s, coefficient=%s', term_id, value, coefficient)
        return value * coefficient if data is not None else None
    return get_value


def impact_value(impact: dict, lookup_col: str) -> float:
    lookup = download_lookup('emission.csv', True)
    values = non_empty_list(map(_emission_value(lookup, lookup_col), impact.get('emissionsResourceUse', [])))
    return list_sum(values) if len(values) > 0 else None

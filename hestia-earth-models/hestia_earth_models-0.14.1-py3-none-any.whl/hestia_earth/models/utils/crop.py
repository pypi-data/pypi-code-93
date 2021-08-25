from hestia_earth.utils.model import find_primary_product
from hestia_earth.utils.lookup import download_lookup, extract_grouped_data, get_table_value, column_name
from hestia_earth.utils.tools import list_sum, safe_parse_float

from .property import get_node_property


def get_crop_grouping(term_id: str):
    lookup = download_lookup('crop.csv', True)
    return get_table_value(lookup, 'termid', term_id, column_name('cropGroupingFAOSTAT'))


def get_N2ON_fertilizer_coeff_from_primary_product(cycle: dict):
    product = find_primary_product(cycle)
    term_id = product.get('term', {}).get('@id') if product else None
    lookup = download_lookup('crop.csv', True)
    percent = get_table_value(lookup, 'termid', term_id, column_name('N2ON_FERT')) if term_id else None
    return safe_parse_float(percent, 0.01)


def _crop_property(term: dict, prop_name: str):
    # as the lookup table might not exist, we are making sure we return `0` in thise case
    try:
        lookup = download_lookup('crop-property.csv', True)
        return safe_parse_float(
            extract_grouped_data(
                get_table_value(lookup, 'termid', term.get('@id'), column_name(prop_name)), 'Avg'
            )
        )
    except Exception:
        return 0


def get_crop_property_value_converted(node: dict, prop_name: str):
    prop = get_node_property(node, prop_name)
    prop_value = prop.get('value', 0) if prop else _crop_property(node.get('term', {}), prop_name)
    return list_sum(node.get('value', [])) * prop_value

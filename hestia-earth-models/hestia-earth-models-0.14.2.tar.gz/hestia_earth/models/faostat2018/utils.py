from hestia_earth.utils.api import download_hestia
from hestia_earth.utils.lookup import download_lookup, get_table_value, column_name, extract_grouped_data_closest_date
from hestia_earth.utils.tools import safe_parse_float

from hestia_earth.models.log import logger
from hestia_earth.models.utils.product import convert_animalProduct_to_unit

LOOKUP_PREFIX = 'region-animalProduct-animalProductGroupingFAO'


def _get_grouping(product: dict):
    lookup = download_lookup('animalProduct.csv', True)
    term_id = product.get('term', {}).get('@id')
    # first, get the term which contains the actual grouping
    term_id = get_table_value(lookup, 'termid', term_id, column_name('animalProductGroupingFAOEquivalent'))
    grouping = get_table_value(lookup, 'termid', term_id, column_name('animalProductGroupingFAO'))
    return grouping, term_id


def product_equivalent_value(product: dict, year: int, country: str):
    grouping, fao_product_id = _get_grouping(product)

    if not grouping:
        return None

    lookup = download_lookup(f"{LOOKUP_PREFIX}-productionQuantity.csv")
    quantity_values = get_table_value(lookup, 'termid', country, column_name(grouping))
    quantity = safe_parse_float(extract_grouped_data_closest_date(quantity_values, year))

    lookup = download_lookup(f"{LOOKUP_PREFIX}-head.csv")
    head_values = get_table_value(lookup, 'termid', country, column_name(grouping))
    head = safe_parse_float(extract_grouped_data_closest_date(head_values, year))

    # quantity is in Tonnes
    value = quantity * 1000 / head if head > 0 else 0

    logger.debug('quantity=%s, head=%s, value=%s', quantity, head, value)

    fao_product_term = download_hestia(fao_product_id)
    fao_product = {'term': fao_product_term, 'value': [value]}

    print(fao_product)

    # use the FAO value to convert it to the correct unit
    dest_unit = product.get('term', {}).get('units')
    return convert_animalProduct_to_unit(fao_product, dest_unit)

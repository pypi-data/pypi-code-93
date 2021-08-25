from hestia_earth.utils.model import find_primary_product
from hestia_earth.utils.lookup import download_lookup, get_table_value, column_name, extract_grouped_data
from hestia_earth.utils.tools import safe_parse_float

from hestia_earth.models.utils.crop import get_crop_grouping


def get_emission_factor(cycle: dict, factor: str):
    site = cycle.get('site', {})
    country_id = site.get('country', {}).get('@id')
    primary_product = find_primary_product(cycle)
    crop_grouping = get_crop_grouping(primary_product.get('term', {}).get('@id')) if primary_product else None

    lookup = download_lookup(f"region-crop-cropGroupingFAOSTAT-{factor}.csv", True)

    data = safe_parse_float(get_table_value(lookup, 'termid', country_id, column_name(crop_grouping)), None) \
        if crop_grouping is not None else None

    # fallback to site.siteType data if possible
    return data or safe_parse_float(
        extract_grouped_data(
            get_table_value(lookup, 'termid', country_id, column_name('NONE')), site.get('siteType')), None)

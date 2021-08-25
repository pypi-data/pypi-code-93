from hestia_earth.utils.lookup import get_table_value, download_lookup, column_name
from hestia_earth.utils.tools import safe_parse_float

TERM_ID = 'residueBurnt'


def _get_default_percent(term_id: str, country_id: str):
    lookup = download_lookup('crop.csv', True)
    crop_grouping = get_table_value(lookup, 'termid', term_id, column_name('cropGroupingResidue'))
    country_burnt_lookup = download_lookup('region-crop-cropGroupingResidue-burnt.csv', True)
    percent = get_table_value(country_burnt_lookup, 'termid', country_id, column_name(crop_grouping)) if crop_grouping \
        else None
    percent = safe_parse_float(percent, None)
    comb_factor = safe_parse_float(
        get_table_value(lookup, 'termid', term_id, 'combustion_factor_crop_residue')
    )
    return percent if comb_factor is None or percent is None else percent * comb_factor


def run(cycle: dict, primary_product: dict):
    term_id = primary_product.get('term', {}).get('@id', '')
    country_id = cycle.get('site', {}).get('country', {}).get('@id')
    value = _get_default_percent(term_id, country_id)
    return None if value is None else value * 100

from hestia_earth.schema import TermTermType
from hestia_earth.utils.lookup import column_name, download_lookup, get_table_value
from hestia_earth.utils.tools import list_sum, safe_parse_float
from hestia_earth.utils.model import filter_list_term_type, find_primary_product

from hestia_earth.models.utils.blank_node import get_total_value
from hestia_earth.models.utils.input import filter_by_term_type_and_lookup, get_total_phosphate

SLOPE_RANGE = [
    [0.0, 0.03, 1.2],
    [0.03, 0.08, 1.0],
    [0.08, 0.12, 1.2],
    [0.12, 0.16, 1.4],
    [0.16, 0.20, 1.6],
    [0.20, 0.24, 1.8],
    [0.24, 0.28, 2.0],
    [0.28, 0.32, 2.2]
]


def get_liquid_slurry_sludge_P_total(cycle: dict):
    inputs = filter_by_term_type_and_lookup(
        cycle.get('inputs', []), TermTermType.ORGANICFERTILIZER,
        col_name='OrganicFertilizerClassification',
        col_value='Liquid, Slurry, Sewage Sludge'
    )
    return list_sum(get_total_phosphate(inputs))


def _get_tillage(cycle: dict):
    tillage_ids = ['fullTillage', 'minimumTillage', 'noTillage']
    practices = cycle.get('practices', [])
    v = next(filter(lambda i: i.get('term', {}).get('@id') in tillage_ids, practices), {})
    return v.get('term', {}).get('@id')


def get_pcorr(slope: float):
    return next((element[2] for element in SLOPE_RANGE if slope >= element[0] and slope < element[1]), None)


def _get_float_from_lookup(lookup_name: str, col: str, term_id: str):
    lookup = download_lookup(lookup_name, True)
    return safe_parse_float(get_table_value(lookup, 'termid', term_id, column_name(col)), None)


def _get_C2_factor(term_id: str):
    return _get_float_from_lookup('landUseManagement.csv', 'C2_FACTORS', term_id)


def get_practice_factor(site: dict):
    country_id = site.get('country', {}).get('@id')
    return _get_float_from_lookup('region.csv', 'Practice_Factor', country_id)


def get_p_ef_c1(cycle: dict):
    primary_product = find_primary_product(cycle)
    product_id = primary_product.get('term', {}).get('@id') if primary_product else None
    return _get_float_from_lookup('crop.csv', 'P_EF_C1', product_id) if product_id else None


def get_ef_p_c2(cycle: dict):
    tillage = _get_tillage(cycle)
    country_id = cycle.get('site', {}).get('country', {}).get('@id')
    # TODO: handle pasture
    return _get_float_from_lookup('region.csv', 'EF_P_C2', country_id) if tillage is None else _get_C2_factor(tillage)


def get_water(cycle: dict, precipitation: float):
    inputs = cycle.get('inputs', [])
    filter_irrigation = filter_list_term_type(inputs, TermTermType.WATER)
    irrigation = list_sum(get_total_value(filter_irrigation))
    return list_sum([irrigation/10, precipitation or 0])


def calculate_R(heavy_winter_precipitation: float, water: float):
    winter_precipitation = 1 if heavy_winter_precipitation > 0 else 0.1
    water_coeff = (587.8 - 1.219 * water) + (0.004105 * water ** 2) if water > 850 else (0.0483 * water ** 1.61)
    return water_coeff * winter_precipitation


def calculate_A(
    R: float,
    practise_factor: float,
    erodability: float,
    slope_length: float,
    pcorr: float,
    p_ef_c1: float,
    ef_p_c2: float
):
    return R * practise_factor * erodability * slope_length * pcorr * p_ef_c1 * ef_p_c2

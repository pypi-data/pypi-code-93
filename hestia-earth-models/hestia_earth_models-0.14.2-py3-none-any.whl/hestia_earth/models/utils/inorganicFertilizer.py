from hestia_earth.utils.lookup import column_name, download_lookup, get_table_value, extract_grouped_data
from hestia_earth.utils.tools import safe_parse_float


def get_terms():
    lookup = download_lookup('inorganicFertilizer.csv', True)
    return list(lookup.termid)


def get_term_lookup(term_id: str, col_name: str):
    lookup = download_lookup('inorganicFertilizer.csv', True)
    return get_table_value(lookup, 'termid', term_id, column_name(col_name))


def _get_temperature_lookup_key(temperature: float):
    return 'cool' if temperature <= 14 else ('temperate' if temperature <= 25 else 'warm')


def _get_soilPh_lookup_key(soilPh: float):
    return 'acidic' if soilPh < 7 else 'basic'


def get_NH3_emission_factor(term_id: str, soilPh: float, temperature: float):
    lookup = download_lookup('inorganicFertilizer.csv', True)
    soilPh_key = _get_soilPh_lookup_key(soilPh)
    temperature_key = _get_temperature_lookup_key(temperature)
    data = get_table_value(lookup, 'termid', term_id, column_name(f"NH3_emissions_factor_{soilPh_key}"))
    return safe_parse_float(extract_grouped_data(data, temperature_key), 1)

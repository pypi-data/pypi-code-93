"""Look up the GIDEON API code for a particular item"""

from typing import Optional, Union
from gideon_api import gideon_api

ENDPOINT_ID_NAME = {
    'disease': ('/diseases', 'disease_code'),
    'agent': ('/diseases/fingerprint/agents', 'agent_code'),
    'vector': ('/diseases/fingerprint/vectors', 'vector_code'),
    'vehicle': ('/diseases/fingerprint/vehicles', 'vehicle_code'),
    'reservoir': ('/diseases/fingerprint/reservoirs', 'reservoir_code'),
    'drug': ('/drugs', 'drug_code'),
    'vaccine': ('/vaccines', 'vaccine_code'),
    'bacteria': ('/microbiology/bacteria', 'bacteria_code'),
    'mycobacteria': ('/microbiology/mycobacteria', 'mycobacteria_code'),
    'yeast': ('/microbiology/yeasts', 'yeast_code'),
    'country': ('/countries', 'country_code'),
    'region': ('/travel/regions', 'region_code'),
}


def lookup_id(category: str, item: str) -> Optional[Union[int, str]]:
    """Looks up the GIDEON ID for a particular item.

    Args:
        category: The GIDEON API to search from such as diseases, vaccines,
            countries, etc.
        item:
            The name of the item, such as a particular disease or bacteria.

    Returns:
        If the item is found, the GIDEON API code
    """
    if category not in ENDPOINT_ID_NAME:
        raise ValueError(
            f"Category must be one of: {', '.join(ENDPOINT_ID_NAME)}.")

    api_endpoint, id_key = ENDPOINT_ID_NAME[category]
    all_category_items = gideon_api.query_gideon_api(api_endpoint,
                                                     try_dataframe=False)

    # All items should be under the 'data' key
    assert 'data' in all_category_items

    # Check for item, expects exact match for now
    search_name = item.strip().lower()
    possible_matches = []

    for catalog_item in all_category_items['data']:
        id_ = catalog_item[id_key]
        name = catalog_item[category]

        if name.strip().lower() == search_name:
            possible_matches.append((id_, name))

    # Ensure only one option matched
    if len(possible_matches) == 1:
        return possible_matches[0][0]

    # Show multiple matches otherwise
    if len(possible_matches) > 1:
        return possible_matches


def lookup_disease_id(disease: str) -> int:
    return lookup_id('disease', disease)


def lookup_agent_id(agent: str) -> int:
    return lookup_id('agent', agent)


def lookup_vector_id(vector: str) -> str:
    return lookup_id('vector', vector)


def lookup_vehicle_id(vehicle: str) -> str:
    return lookup_id('vehicle', vehicle)


def lookup_reservoir_id(reservoir: str) -> str:
    return lookup_id('reservoir', reservoir)


def lookup_drug_id(drug: str) -> int:
    return lookup_id('drug', drug)


def lookup_vaccine_id(vaccine: str) -> int:
    return lookup_id('vaccine', vaccine)


def lookup_bacteria_id(bacteria: str) -> int:
    return lookup_id('bacteria', bacteria)


def lookup_mycobacteria_id(mycobacteria: str) -> int:
    return lookup_id('mycobacteria', mycobacteria)


def lookup_yeast_id(yeast: str) -> int:
    return lookup_id('yeast', yeast)


def lookup_country_id(country: str) -> str:
    return lookup_id('country', country)


def lookup_region_id(region: str) -> int:
    return lookup_id('region', region)

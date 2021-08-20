"""GIG Nearby."""

from utils import db, geo
from utils.cache import cache

from gig._constants import EXCLUDE_PLACE_IDS, GIG_CACHE_NAME, GIG_CACHE_TIMEOUT
from gig.ent_types import NEARBY_ENTITY_TYPES
from gig.ents import get_entities


@cache(GIG_CACHE_NAME, GIG_CACHE_TIMEOUT)
def get_nearby_entities(
    lat_lng,
    distance_limit=20,
    nearby_entity_limit=10,
):
    """Get entities that are nearby a given location.

    Args:
        lat_lng (lat, lng): Location
        distance_limit(int, optional): Distance limit in km. Default = 20km
        nearby_entity_limit (int, optional):  Maximum number of entities
            to return. Default = 10
    Returns:
        entities

    .. code-block:: python

        >> from gig import nearby
        >> lat_lng = 6.9073, 79.8638  # Cinnamon Gardens Police Station
        >> nearby.get_nearby_entities(lat_lng, 1, 1)
        [{
            'distance': 0.0024287328123487,
            'entity_type': 'ps',
            'entity': {
                'province': 'Western', 'province_id': 'LK-1',
                'district_id': 'LK-11', 'division_id': 'PS-1103',
                'ps_id': 'PS-110324', 'division': 'Colombo South',
                'num': '24', 'name': 'Cinnamon Garden',
                'lat': '6.9072887', 'lng': '79.86381899999999',
                'phone_mobile': '071-8591588',
                'phone_office': '011-2693377', 'fax': '011-2695411'}}]
    """
    distance_info_list = []
    for entity_type in NEARBY_ENTITY_TYPES:
        id_key = db.get_id_key(entity_type)
        entities = get_entities(entity_type)
        for entity in entities:
            entity_id = entity.get(id_key, None)
            if not entity_id or entity_id in EXCLUDE_PLACE_IDS:
                continue
            lat_lng1 = (float)(entity['lat']), (float)(entity['lng'])
            distance = geo.get_distance(lat_lng, lat_lng1)
            if distance <= distance_limit:
                distance_info_list.append(
                    {
                        'distance': distance,
                        'entity_type': entity_type,
                        'entity': entity,
                    }
                )
    distance_info_list = sorted(
        distance_info_list,
        key=lambda x: x['distance'],
    )
    if len(distance_info_list) > nearby_entity_limit:
        distance_info_list = distance_info_list[:nearby_entity_limit]

    return distance_info_list

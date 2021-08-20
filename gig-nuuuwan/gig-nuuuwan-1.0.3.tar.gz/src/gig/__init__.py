"""GIG (short for Generalized Information Graph) is a graph that is capable of
storing generic information. As of now, all the information stored in GIG
is information pertaining to Sri Lanka.

Information is organized by entities, which have a unique entity id. And entity
can be accessed using its entity id.

.. code-block:: python

    >> from gig import entities
    >> entities.get_entity('LK-11')
    {'district_id': 'LK-11', 'name': 'Colombo', 'province_id': 'LK-1',
    'ed_id': 'EC-01', 'hasc': 'LK.CO', 'fips': 'CE23',
    'area': '642', 'population': '2324349'}

Each entity belongs to a particular entity type. The entity id value is keyed
in format <entity_type>_id. Hence, in the above example, the "Colombo District"
entity has entity type *district*, and its entity id is stored in field
*district_id*.

An entity's entity type can be uniquely identified from its entity id, or via
the following convinience function.

.. code-block:: python

    >> from gig.ent_types import get_entity_type
    >> get_entity_type('LK-11')  # Colombo District
    'district'


All entities belonging to a particular type can be accessed with
*get_entities*. However, this should be used with caution, as some entity
types might have a large number of entities.

.. code-block:: python

    >> from gig import entities
    >> ents = entities.get_entities('province')
    >> ents[0]
    {'province_id': 'LK-1', 'name': 'Western',
    'country_id': 'LK', 'fips': 'CE36', 'area': '3709',
    'capital': 'Colombo'}

*get_entity_index* is similar to *get_entities* and returns all entities
of a particular type, indexed by entity id.

.. code-block:: python

    >> from gig import entities
    >> entity_index = entities.get_entity_index('province')
    >> entity_index['LK-2']
    {'province_id': 'LK-2', 'name': 'Central',
    'country_id': 'LK', 'fips': 'CE29', 'area': '5584', 'capital': 'Kandy'}

*get_entity_ids* can be used to get all entity ids of a particular type.

.. code-block:: python

    >> from gig import entities
    >> entities.get_entity_ids('province')
    ['LK-1', 'LK-2', 'LK-3', 'LK-4', 'LK-5', 'LK-6',
    'LK-7', 'LK-8', 'LK-9']

Some entities (like "Police Stations" - 'ps'), have an associated location.
All such entities nearby a particular location can be accessed using
*get_nearby_entities* in the *nearby* module.

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

*get_entity* and related functions provide only basic information about
an entity. The *ext_data* module provides access to extended data.

Extended data is organized in groups, each of which contains several tables.
For example, census data is in data_group *census*, which contains 26
stables including "total_population".

The census table "total_population" for Colombo District can be accessed as
follows:

.. code-block:: python

    >> from gig.ext_data import get_table_data
    >> get_table_data('census', 'total_population', ['LK-11'])
    {'LK-11': {'entity_id': 'LK-11', 'total_population': 2323964.0}}

Also, currently, this data is stored in a set of TSV and JSON files in
https://github.com/nuuuwan/gig-data. We plan to optimize this storage in the
future.

"""

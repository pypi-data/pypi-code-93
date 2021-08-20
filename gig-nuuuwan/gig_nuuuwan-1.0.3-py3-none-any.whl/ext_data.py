"""Utils for accessing extended entity attributes.

Module *entities* enables access to basic entity data. For example, the
following information can be access about Colombo District.

.. code-block:: python

    >> from gig import entities
    >> entities.get_entity('district', 'LK-11')
    {'district_id': 'LK-11', 'name': 'Colombo', 'province_id': 'LK-1',
    'ed_id': 'EC-01', 'hasc': 'LK.CO', 'fips': 'CE23',
    'area': '642', 'population': '2324349'}

This module (ext_data) enables access to more elaborate data, like census data.

Extended data is organized in groups, each of which contains several tables.
For example, census data is in data_group *census*, which contains 26
stables including "total_population".

The census table "total_population" for Colombo District can be accessed as
follows:

.. code-block:: python

    >> from gig.ext_data import get_table_data
    >> get_table_data('census', 'total_population', ['LK-11'])
    {'LK-11': {'entity_id': 'LK-11', 'total_population': 2323964.0}}

"""
from utils import dt
from utils.cache import cache

from gig._constants import GIG_CACHE_NAME, GIG_CACHE_TIMEOUT
from gig._remote_data import _get_remote_json_data, _get_remote_tsv_data
from gig.ent_types import get_entity_type


@cache(GIG_CACHE_NAME, GIG_CACHE_TIMEOUT)
def _get_meta_data(data_group):
    """Get attr table index."""
    return _get_remote_json_data('%s/meta.json' % data_group)


@cache(GIG_CACHE_NAME, GIG_CACHE_TIMEOUT)
def _get_table(data_group, table_id):
    """Get table."""
    table = _get_remote_tsv_data(
        '%s/data.%s.tsv'
        % (
            data_group,
            table_id,
        )
    )

    return list(
        map(
            lambda row: dict(
                zip(
                    row.keys(),
                    list(map(lambda v: dt.parse_float(v, v), row.values())),
                )
            ),
            table,
        )
    )


@cache(GIG_CACHE_NAME, GIG_CACHE_TIMEOUT)
def _get_table_index(data_group, table_id):
    """Get attr table."""
    table = _get_table(data_group, table_id)
    return dict(
        zip(
            list(map(lambda d: d['entity_id'], table)),
            table,
        )
    )


@cache(GIG_CACHE_NAME, GIG_CACHE_TIMEOUT)
def get_table_data(data_group, table_id, entity_ids=None, entity_type=None):
    """Get data for a given data_group, table and entity selection.

    Args:
        data_group(str): Attribute group
        table_id(str): Table id
        entity_ids(list, optional): Entity IDs to get attributes
        entity_type(str, optional): Gets attributes for all entities of this
            entity type. Ignored if *entity_ids* is specified
    Returns:
        Map of entity id to attributes

    .. code-block:: python

        >> from gig.ext_data import get_table_data
        >> get_table_data('census', 'total_population', ['LK'])
        {'LK': {'entity_id': 'LK', 'total_population': 20359054.0}}

        >> get_table_data('census', 'total_population', entity_type='province')
        {'LK-1': {'entity_id': 'LK-1', 'total_population': 5850745.0},
        'LK-2': {'entity_id': 'LK-2', 'total_population': 2571557.0},
        'LK-3': {'entity_id': 'LK-3', 'total_population': 2477285.0},
        'LK-4': {'entity_id': 'LK-4', 'total_population': 1061315.0},
        'LK-5': {'entity_id': 'LK-5', 'total_population': 1555510.0},
        'LK-6': {'entity_id': 'LK-6', 'total_population': 2380861.0},
        'LK-7': {'entity_id': 'LK-7', 'total_population': 1266663.0},
        'LK-8': {'entity_id': 'LK-8', 'total_population': 1266463.0},
        'LK-9': {'entity_id': 'LK-9', 'total_population': 1928655.0}}


    """
    table_index = _get_table_index(data_group, table_id)
    if entity_ids:
        data_map = {}
        for entity_id in entity_ids:
            data_map[entity_id] = table_index.get(entity_id, {})
        return data_map

    if entity_type:
        data_map = {}
        for entity_id, data in table_index.items():
            entity_type0 = get_entity_type(entity_id)
            if entity_type == entity_type0:
                data_map[entity_id] = data
        return data_map

    return table_index

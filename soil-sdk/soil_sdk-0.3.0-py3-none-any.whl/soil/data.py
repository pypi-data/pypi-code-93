''' Defines soil.data()'''
from typing import Any, Dict, Optional
from soil.api import get_result, upload_data, get_alias
from soil.data_structure import DataStructure, _get_data_structure_name_and_serialize


def data(data_object: Any, metadata: Optional[Dict[str, Any]] = None) -> DataStructure:
    ''' Load data from the cloud or mark it as uploadable '''
    if isinstance(data_object, str):
        # Data object is an id or an alias
        try:
            data_object = _load_data_alias(data_object)
        except KeyError:
            pass
        return _load_data_id(data_object)
    return _upload_data(data_object, metadata)


def _upload_data(data_object: Any, metadata: Optional[Dict[str, Any]] = None) -> DataStructure:
    ds_name, serialized = _get_data_structure_name_and_serialize(data_object)
    result = upload_data(ds_name, serialized, metadata)
    ds = DataStructure(result['_id'], dstype=result['type'])
    return ds


def _load_datastructure(did: str, dtype: str) -> DataStructure:
    # TODO dynamically load a data structure
    return DataStructure(did, dstype=dtype)


def _load_data_alias(alias: str) -> str:
    return get_alias(alias)['state']['result_id']


def _load_data_id(data_id: str) -> DataStructure:
    result = get_result(data_id)
    return _load_datastructure(result['_id'], result['type'])

'''
This package contains calls for soil alias data structures
'''
from typing import List, Optional
from soil.api import set_alias
from soil.data_structure import DataStructure


def alias(name: str, data_ref: DataStructure, roles: Optional[List[str]] = None) -> None:
    ''' Set an alias to a data reference'''
    # Force to get an id if there is none yet.
    if data_ref.id is None:
        data_ref.get_id()
    assert isinstance(data_ref.id, str)
    set_alias(name, data_ref.id, roles)

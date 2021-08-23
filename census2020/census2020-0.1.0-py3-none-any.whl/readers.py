from pathlib import Path
from typing import Dict, List, Optional, Tuple, TypeVar, Union

import pyarrow as pa
import pyarrow.dataset as ds
import us

from census2020.types import FilenameType

T = TypeVar("T")


def _wrap_list(opt: Optional[Union[T, List[T], Tuple[T, ...]]]) -> List[T]:
    if opt is None:
        return []
    if isinstance(opt, (list, tuple)):
        return list(opt)
    return [opt]


def read_filtered_dataset(
    filename: FilenameType,
    states: Optional[Union[str, List[str]]] = None,
    levels: Optional[Union[str, List[str]]] = None,
    columns: Optional[Union[str, List[str]]] = None,
) -> pa.Table:
    basedir = Path(filename)

    states = _wrap_list(states)
    state_objs = [us.states.lookup(state) for state in states]
    if state_objs:
        paths: Union[Path, List[Path]] = [
            basedir / f"{state.abbr.lower()}.parquet" for state in state_objs
        ]
    else:
        paths = basedir

    dataset = ds.dataset(paths, format="parquet")

    filter_expression = ds.scalar(1) == ds.scalar(1)
    levels = _wrap_list(levels)
    if levels:
        filter_expression &= ds.field("SUMLEV").isin(levels)

    columns = _wrap_list(columns)
    if columns:
        d_columns: Dict[str, ds.Expression] = {}

        # Insert default columns. For now just GEOID
        for key in ["GEOID"]:
            if key not in columns:
                d_columns[key] = ds.field(key)

        # Append all other columns
        d_columns.update({key: ds.field(key) for key in columns})
        kwarg_columns: Optional[Dict[str, ds.Expression]] = d_columns
    else:
        kwarg_columns = None

    return dataset.to_table(filter=filter_expression, columns=kwarg_columns)

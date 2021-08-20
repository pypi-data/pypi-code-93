from collections.abc import Iterable
from functools import reduce
from typing import List, Any, Union, Iterable

from bson.objectid import ObjectId
from pandas import DataFrame, concat, Series, merge


def bson_to_string(df: DataFrame) -> DataFrame:
    for column in df.columns:
        if not df[column].dropna().empty and isinstance(
                df.at[df[column].first_valid_index(), column], ObjectId):
            df[column] = df[column].astype("str")
    return df


def flatten(df: DataFrame) -> DataFrame:
    def _get_nested_columns(frame: DataFrame):
        columns = []
        for col in frame.columns:
            if not frame[col].dropna().empty and isinstance(
                    frame.at[frame[col].first_valid_index(), col], dict):
                columns.append(col)
        return columns

    def unpack(df: DataFrame, columns: list) -> DataFrame:
        storage = []
        for column in columns:
            df[column] = df[column].fillna({})
            placeholder = lambda val:{True: "{}{}", False: "{}_{}"}.get(val)
            tmp = df[column].apply(Series, dtype="object")

            if 0 in tmp.columns:
                tmp = tmp.drop(0, axis=1)

            storage.append(
                tmp.rename(
                    columns={c: placeholder(c.startswith("_")).format(
                        column, c) for c in tmp.columns}
                )
            )
        return concat([df.drop(columns, axis=1)]+storage, axis=1)

    nested_columns = _get_nested_columns(df.reset_index(drop=True))
    result = unpack(df.reset_index(drop=True), nested_columns)

    return result


def chunkize(data: List[Any], size: int = 5000) -> Iterable:
    if size <= 0:
        raise ValueError("param size must be greater than 0")    
    return (
        data[position:position+size] 
        for position  in range(0, len(data), size)
    )


def merger(*args) -> DataFrame:
    return reduce(lambda left, right: [merge(left[0], right[0], **right[1])], args)[0]


def str_to_bson(data: Union[str, List[str]]) -> List[ObjectId]:
    if isinstance(data, str):
        return ObjectId(data)
    elif isinstance(data, Iterable):
        if len(data) == 0:
            raise ValueError("List size shouldn't equal zero.")
        return [ObjectId(value) for value in data]
    else:
        raise ValueError("value should be single string or list of strings")
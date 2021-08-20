from datetime import date
import enum
from io import StringIO
import logging
from typing import Any, Dict, Iterable, List, Optional

import pandas as pd


logger = logging.getLogger(__name__)


def filter_nones_from_dict(query_parameters: Dict[str, Optional[Any]]) -> Dict[str, Any]:
    """
    This function takes a list of parameters as a dict, and returns a dict containing only non null parameters

    Examples:
        >>> filter_nones_from_dict({"key1": None, "key2": "some value"})
        {"key2": "some value"}

    Args:
        query_parameters (dict): query parameters in the form of a dict with `None` values

    Returns:
        dict: a dict with None values filtered

    """
    return {k: v for k, v in query_parameters.items() if v}


def process_list_parameter(parameter: Optional[List[str]]) -> Optional[str]:
    return convert_list_to_string_query_params(parameter) if parameter else None


def process_bool_parameter(parameter: Optional[bool]) -> Optional[str]:
    return str(parameter).lower() if parameter is not None else None


def process_date_parameter(parameter: Optional[date]) -> Optional[str]:
    return parameter.isoformat() if parameter else None


def process_enum_parameters(
    parameter: Optional[List[enum.Enum]], to_lower_case: bool = True
) -> Optional[str]:
    return (
        convert_list_to_string_query_params(
            [p.value.lower() if to_lower_case else p.value for p in parameter]
        )
        if parameter
        else None
    )


def process_enum_parameter(
    parameter: Optional[enum.Enum], to_lower_case: bool = True
) -> Optional[str]:
    return (
        (str(parameter.value.lower()) if to_lower_case else str(parameter.value))
        if parameter
        else None
    )


def convert_list_to_string_query_params(list_of_parameters: Iterable[str]) -> str:
    if type(list_of_parameters) in (list, tuple):
        return ",".join(list_of_parameters)
    else:
        # list_of_parameters is already string here
        # but let's cast it other the tests are failing
        return str(list_of_parameters)


def prepare_pandas_mapping(mapping: Dict[str, Any]):
    """
    Will return 3 dict that contains the mapping Kpler -> mapping pandas
    We return N lists because we need to handle the conversion differently.

    The lists:
    1. mapping for integer
    2. mapping for booleans
    3. mapping for others
    """
    mapping_int = {}
    mapping_bool = {}
    mapping_oth = {}
    for c, _type in mapping.items():
        if _type == "integer":
            mapping_int[c] = "int32"
        elif _type == "long":
            mapping_int[c] = "int64"
        elif _type == "boolean":
            mapping_bool[c] = "bool"
        elif _type == "float":
            mapping_oth[c] = "float"
        elif _type == "double":
            mapping_oth[c] = "float64"
        elif _type == "date yyyy-MM-dd":
            mapping_oth[c] = "datetime64[D]"
        elif _type == "datetime yyyy-MM-dd HH:mm":
            mapping_oth[c] = "datetime64[m]"
        # else it's object (for strings)
    return (mapping_int, mapping_bool, mapping_oth)


def bytes_to_pandas_data_frame(byte_contents: bytes, mapping: Dict[str, Any]) -> pd.DataFrame:
    """
    Will convert bytes content to a Pandas dataframe

    - If the mapping is given (not empty), then we just read the dataframe without type infering.
    We then apply the mapping coming from the get_columns endpoint.
    - If the mapping is not given, then we create the dataframe with type infering. But we try to
    set datetime types manually behind just in case.
    """
    if len(mapping) > 0:
        df = pd.read_csv(
            StringIO(byte_contents.decode("utf-8")),
            sep=";",
            dtype="object",
        )
        (mapping_int, mapping_bool, mapping_oth) = prepare_pandas_mapping(mapping)

        # we split the mapping between integer and the others
        # because the mapping to integer can fail because of NA values -> map to float
        columns_in_endpoint_int = {c: mapping_int[c] for c in df.columns if c in mapping_int}
        columns_in_endpoint_bool = {c: mapping_bool[c] for c in df.columns if c in mapping_bool}
        columns_in_endpoint_oth = {c: mapping_oth[c] for c in df.columns if c in mapping_oth}
        # array that contains the columns for which the integer mapping failed
        columns_to_float = []

        try:
            # this mapping should not fail
            df = df.astype(columns_in_endpoint_oth)
            # for boolean, since KPLER API returns "true/false", this is evaluated as a non-null value,
            # hence always TRUE for a pandas boolean. So we need to tweak that a bit.
            for col in columns_in_endpoint_bool:
                df[col] = df[col].str.lower() == "true"
        except Exception as e:
            logger.error(f"[pandas] Error while casting resulting dataframe: {e}")

        for col, _type in columns_in_endpoint_int.items():
            try:
                df[col] = df[col].astype(_type)
            except Exception:
                # failed for integer, not really an error, let's try float
                columns_to_float.append(col)

        for col in columns_to_float:
            try:
                df[col] = df[col].astype("float64")
            except Exception as e:
                logger.error(f"[pandas] Cast to int/float failed for '{col}': {e}")

    else:
        df = pd.read_csv(
            StringIO(byte_contents.decode("utf-8")),
            sep=";",
            low_memory=False,
        )
        # let's convert the dates if possible
        # we have at least ETA or date in the column name
        cols_dates = [
            col
            for col in df.columns
            if any([p.lower() in col.lower() for p in ("from", "until", "date", "eta")])
            and str(df[col].head(1).values).count("-")
            > 1  # Adding this to avoid converting i.e 2016-02 to 2016-02-01
        ]
        for col in cols_dates:
            try:
                df[col] = pd.to_datetime(df[col])
            except Exception as e:
                logger.error(f"[pandas] Cast to datetime failed for '{col}': {e}")

    return df

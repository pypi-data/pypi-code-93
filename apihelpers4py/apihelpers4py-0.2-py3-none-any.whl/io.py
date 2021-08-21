from base64 import b64decode, b64encode
from io import StringIO
from typing import Dict, List, Optional
from urllib import parse

import pandas as pd

ISO_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.%f%z"


def dataframe_to_csv_base64(
    df: pd.DataFrame, sep: str = ";", date_format: str = ISO_DATE_FORMAT
) -> str:
    csv_data = df.to_csv(
        index=True,
        sep=sep,
        date_format=date_format,
        encoding="utf-8",
        line_terminator="\n",
    )
    return b64encode(csv_data.encode()).decode()


def csv_base64_to_dataframe(b64_csv_data: str, sep=";") -> pd.DataFrame:
    str_data = StringIO(b64decode(b64_csv_data.encode()).decode())
    return pd.read_csv(str_data, sep=sep, infer_datetime_format=True)


def extract_parameters_from_url(url: str) -> Dict:
    params = dict(parse.parse_qsl(parse.urlsplit(url).query))
    return params


def string_to_list(s: str, sep: str = ",", dtype: Optional[str] = None) -> List:
    l_in = s.split(sep)
    if (dtype is None) or (dtype == "str"):
        out = l_in
    elif dtype == "int":
        out = [int(i) for i in l_in]
    elif dtype == "float":
        out = [float(i) for i in l_in]
    else:
        raise ValueError("Illegal value for dtype ({dtype})")
    return out

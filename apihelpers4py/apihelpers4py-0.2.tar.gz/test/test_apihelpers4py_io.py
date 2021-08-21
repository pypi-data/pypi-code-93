from datetime import datetime

import pandas as pd
from dateutil.tz import gettz as timezone
import pytest

utc = timezone("UTC")


def test_time():
    from apihelpers4py.io import ISO_DATE_FORMAT

    t0 = datetime.now().replace(microsecond=0)
    t0_str = t0.strftime(ISO_DATE_FORMAT)
    t1 = datetime.fromisoformat(t0_str)
    isinstance(t0_str, str)
    assert t0 == t1

    tz = timezone("Europe/Copenhagen")
    t0_tz = datetime.now(tz=tz).replace(microsecond=0)
    t0_tz_str = t0_tz.strftime(ISO_DATE_FORMAT)

    t0_tz_str2 = t0_tz_str[0:-2] + ":" + t0_tz_str[-2:]
    t1_tz = datetime.fromisoformat(t0_tz_str2)
    isinstance(t0_tz_str, str)
    assert t0_tz == t1_tz
    assert t0_tz.astimezone(utc) == t1_tz.astimezone(utc)


def test_df_base64():
    from apihelpers4py.io import csv_base64_to_dataframe, dataframe_to_csv_base64

    tz = timezone("Europe/Copenhagen")

    __t = pd.date_range("2021-01-01", "2021-01-05", freq="1H", tz=tz)
    __price_t = __t.hour
    df = pd.DataFrame(
        {"local_demand": 0, "local_production": 0, "power_price": __price_t}, index=__t
    )

    df_str = dataframe_to_csv_base64(df)
    df2 = csv_base64_to_dataframe(df_str)
    assert isinstance(df_str, str)
    assert isinstance(df2, pd.DataFrame)

    # TODO : fix this part
    df2.set_index(__t, inplace=True)
    df2.drop(columns=["Unnamed: 0"], inplace=True)
    pd.testing.assert_frame_equal(df, df2)


def test_reformat():
    from apihelpers4py.io import extract_parameters_from_url, string_to_list

    s = extract_parameters_from_url(
        "http://www.google.com?hello=world&abc=2&list=1,2,3"
    )
    assert s["hello"] == "world"
    assert s["abc"] == "2"
    assert s["list"] == "1,2,3"

    assert string_to_list("1,2,3") == ["1", "2", "3"]
    assert string_to_list("1,2,3", dtype="str") == ["1", "2", "3"]
    assert string_to_list("1,2,3", dtype="int") == [1, 2, 3]
    assert string_to_list("1,2,3", dtype="float") == [1.0, 2.0, 3.0]

    with pytest.raises(ValueError):
        string_to_list("1,2,3", dtype="erroneous_type")

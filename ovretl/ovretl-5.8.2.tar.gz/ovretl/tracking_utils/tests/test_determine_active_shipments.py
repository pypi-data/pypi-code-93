import pandas as pd
import os
from pandas.util.testing import assert_frame_equal

from ovretl.tracking_utils.determine_active_shipments import determine_active_shipments

cwd = os.path.dirname(__file__)


def test_determine_active_shipments():
    raw_df = pd.read_csv(os.path.join(cwd, "shipments_clean.csv"), parse_dates=True)
    raw_df.loc[:, "delivery_date"] = pd.to_datetime(raw_df["delivery_date"])
    raw_df.loc[:, "arrival_date"] = pd.to_datetime(raw_df["arrival_date"])
    result = determine_active_shipments(raw_df, "2020-09-17")
    result_should_be = pd.read_csv(os.path.join(cwd, "active_shipments.csv"), parse_dates=True)
    assert_frame_equal(
        result.reset_index(drop=True),
        result_should_be.reset_index(drop=True),
        check_dtype=False,
        check_column_type=False,
        check_less_precise=True,
        check_names=False,
        check_exact=False,
        check_datetimelike_compat=True,
    )

import os

import pandas as pd
from pandas.util.testing import assert_frame_equal
from ovretl.performances_utils.calculate_shipments_treatment_steps_time import calculate_shipments_treatment_steps_time

cwd = os.path.dirname(__file__)


def test_calculate_shipments_treatment_steps_time():
    events_shipment_df = pd.read_csv(os.path.join(cwd, "./events_shipment.csv"))
    activities_clean_df = pd.read_csv(os.path.join(cwd, "./activities_clean.csv"))
    shipments_df = pd.read_csv(os.path.join(cwd, "./shipments_df.csv"))
    result = calculate_shipments_treatment_steps_time(
        events_shipment_df=events_shipment_df, activities_clean_df=activities_clean_df, shipments_df=shipments_df,
    )
    result_should_be = pd.read_csv(
        os.path.join(cwd, "shipments_treatment_steps_time.csv"), parse_dates=[i for i in range(1, 11)]
    )
    assert_frame_equal(
        result.sort_values("shipment_id").reset_index(drop=True).fillna(0),
        result_should_be.sort_values("shipment_id").reset_index(drop=True).fillna(0),
        check_dtype=False,
        check_column_type=False,
        check_less_precise=True,
        check_names=False,
        check_exact=False,
        check_datetimelike_compat=True,
    )

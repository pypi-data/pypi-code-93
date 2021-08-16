import os

import pandas as pd
from ovretl.prices_utils.add_prices_to_shipments import add_prices_to_shipments
from pandas.util.testing import assert_frame_equal

columns_to_test = [
    "foresea_name",
    "margin_without_insurance",
    "margin_insurance",
    "turnover",
    "departure_truck_freight_price",
    "departure_fees_price",
    "freight_price",
    "arrival_fees_price",
    "arrival_truck_freight_price",
    "customs_price",
    "insurance_price",
    "vat_price",
    "other_price",
    "departure_truck_freight_purchase_price",
    "departure_fees_purchase_price",
    "freight_purchase_price",
    "arrival_fees_purchase_price",
    "arrival_truck_freight_purchase_price",
    "insurance_purchase_price",
]

cwd = os.path.dirname(__file__)


def test_add_prices_to_shipments():
    shipments_df = pd.read_csv(os.path.join(cwd, "shipments_loads.csv"))
    final_checks_df = pd.read_csv(os.path.join(cwd, "final_checks_clean.csv"))
    billings_df = pd.read_csv(os.path.join(cwd, "billings_clean.csv"))
    prices_final_check_by_category_df = pd.read_csv(os.path.join(cwd, "prices_final_check_by_category.csv"))
    prices_billings_by_category_df = pd.read_csv(os.path.join(cwd, "prices_billings_by_category.csv"))
    prices_propositions_by_category_df = pd.read_csv(os.path.join(cwd, "prices_by_category.csv"))
    result = add_prices_to_shipments(
        shipments_df=shipments_df,
        final_checks_df=final_checks_df,
        billings_df=billings_df,
        prices_final_check_by_category_df=prices_final_check_by_category_df,
        prices_billings_by_category_df=prices_billings_by_category_df,
        prices_propositions_by_category_df=prices_propositions_by_category_df,
    )
    result_should_be = pd.read_csv(os.path.join(cwd, "result_should_be.csv"))

    assert_frame_equal(
        result[columns_to_test].sort_values("foresea_name").reset_index(drop=True),
        result_should_be[columns_to_test].sort_values("foresea_name").reset_index(drop=True).fillna(0),
    )

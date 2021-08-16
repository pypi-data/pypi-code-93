import pandas as pd

from ovretl import add_category_prices_to_shipments
from ovretl.prices_utils.add_prices_ids_to_shipments import add_prices_ids_to_shipments
from ovretl.prices_utils.features_functions.calculate_category_prices import pivot_category_prices
from ovretl.prices_utils.features_functions.calculate_margins import (
    calculate_margin_without_insurance,
    calculate_margin_insurance,
)
from ovretl.prices_utils.features_functions.calculate_turnover import calculate_turnover
from ovretl.prices_utils.features_functions.calculate_vat import calculate_vat
from ovretl.prices_utils.features_functions.determine_prices_origin import determine_prices_origin
from ovretl.prices_utils.features_functions.merge_all_features import merge_all_features

columns_prices = [
    "initial_margin_without_insurance",
    "initial_margin_insurance",
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
    "departure_truck_freight_initial_price",
    "departure_fees_initial_price",
    "freight_initial_price",
    "arrival_fees_initial_price",
    "arrival_truck_freight_initial_price",
    "insurance_initial_price",
    "departure_truck_freight_initial_purchase_price",
    "departure_fees_initial_purchase_price",
    "freight_initial_purchase_price",
    "arrival_fees_initial_purchase_price",
    "arrival_truck_freight_initial_purchase_price",
    "insurance_initial_purchase_price",
    "departure_truck_freight_purchase_price",
    "departure_fees_purchase_price",
    "freight_purchase_price",
    "arrival_fees_purchase_price",
    "arrival_truck_freight_purchase_price",
    "insurance_purchase_price",
]


def add_prices_to_shipments(
    shipments_df: pd.DataFrame,
    final_checks_df: pd.DataFrame,
    billings_df: pd.DataFrame,
    prices_final_check_by_category_df: pd.DataFrame,
    prices_billings_by_category_df: pd.DataFrame,
    prices_propositions_by_category_df: pd.DataFrame,
) -> pd.DataFrame:
    shipments_with_prices_ids = add_prices_ids_to_shipments(
        shipments_df=shipments_df, final_checks_df=final_checks_df, billings_df=billings_df,
    )
    shipments_with_category_prices_df = add_category_prices_to_shipments(
        shipments_with_prices_ids,
        prices_final_check_by_category_df,
        prices_billings_by_category_df,
        prices_propositions_by_category_df,
    )

    prices_origin_df = determine_prices_origin(shipments_with_category_prices_df)
    turnover_df = calculate_turnover(shipments_with_category_prices_df)
    vat_df = calculate_vat(shipments_with_category_prices_df)
    margin_without_insurance_df = calculate_margin_without_insurance(shipments_with_category_prices_df)
    margin_insurance_df = calculate_margin_insurance(shipments_with_category_prices_df)
    category_prices_df = pivot_category_prices(shipments_with_category_prices_df)

    shipments_df = merge_all_features(
        shipments_df,
        prices_origin_df=prices_origin_df,
        turnover_df=turnover_df,
        vat_df=vat_df,
        margin_without_insurance_df=margin_without_insurance_df,
        margin_insurance_df=margin_insurance_df,
        category_prices_df=category_prices_df,
    )
    shipments_df.loc[:, columns_prices] = shipments_df[columns_prices].fillna(0)
    return shipments_df

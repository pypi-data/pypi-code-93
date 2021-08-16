import pandas as pd


def merge_all_features(
    shipments_df: pd.DataFrame,
    prices_origin_df: pd.DataFrame,
    turnover_df: pd.DataFrame,
    vat_df: pd.DataFrame,
    margin_without_insurance_df: pd.DataFrame,
    margin_insurance_df: pd.DataFrame,
    category_prices_df: pd.DataFrame,
) -> pd.DataFrame:
    shipments_df = pd.merge(
        shipments_df, prices_origin_df[["shipment_id", "prices_origin"]], on="shipment_id", how="left",
    )

    shipments_df = pd.merge(
        shipments_df, turnover_df[["shipment_id", "turnover", "turnover_initial"]], on="shipment_id", how="left",
    )

    shipments_df = pd.merge(shipments_df, vat_df[["shipment_id", "vat_price"]], on="shipment_id", how="left",)

    shipments_df = pd.merge(
        shipments_df,
        margin_without_insurance_df[["shipment_id", "margin_without_insurance", "initial_margin_without_insurance",]],
        on="shipment_id",
        how="left",
    )

    shipments_df = pd.merge(
        shipments_df,
        margin_insurance_df[["shipment_id", "margin_insurance", "initial_margin_insurance"]],
        on="shipment_id",
        how="left",
    )

    return pd.merge(shipments_df, category_prices_df, on="shipment_id", how="left",)

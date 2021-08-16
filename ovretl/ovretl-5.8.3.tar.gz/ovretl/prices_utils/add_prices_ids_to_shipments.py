import pandas as pd


def add_prices_ids_to_shipments(shipments_df: pd.DataFrame, final_checks_df: pd.DataFrame, billings_df: pd.DataFrame):
    shipments_with_ids = shipments_df[["shipment_id", "proposition_id", "foresea_name"]]
    shipments_with_ids = pd.merge(
        shipments_with_ids,
        final_checks_df[["shipment_id", "id", "initial_proposition_id"]],
        on="shipment_id",
        how="left",
    ).rename(columns={"id": "final_check_id"})

    shipments_with_ids = pd.merge(
        shipments_with_ids, billings_df[["shipment_id", "id"]], on="shipment_id", how="left",
    ).rename(columns={"id": "billing_id"})

    return shipments_with_ids[
        ~shipments_with_ids.duplicated(subset=["final_check_id"]) | shipments_with_ids["final_check_id"].isnull()
    ]

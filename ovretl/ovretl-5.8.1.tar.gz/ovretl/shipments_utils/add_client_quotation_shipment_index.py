import pandas as pd
import numpy as np

SHIPMENT_STRICT_STATUS = ["booking_request", "awaiting_booking", "booked", "in_progress", "finished", "arrived"]


def sort_and_index_group(group: pd.DataFrame):
    sorted_group = group.sort_values("created_at", ascending=True)
    sorted_group.index = np.arange(1, len(sorted_group) + 1)
    return sorted_group


def add_client_order_index(quotation_df: pd.DataFrame, index_column: str):
    quotation_df = quotation_df.groupby(["client_name"]).apply(lambda g: sort_and_index_group(g))
    quotation_df = quotation_df.drop(columns="client_name").reset_index()
    quotation_df = quotation_df.rename(columns={"level_1": index_column})
    return quotation_df


def add_client_quotation_shipment_index(quotation_df: pd.DataFrame) -> pd.DataFrame:
    quotation_df = add_client_order_index(quotation_df, index_column="quotation_number")
    shipments_df = quotation_df[quotation_df["shipment_status"].isin(SHIPMENT_STRICT_STATUS)].copy()
    shipments_df = add_client_order_index(shipments_df, index_column="shipment_number")

    return pd.merge(quotation_df, shipments_df[["foresea_name", "shipment_number"]], on="foresea_name", how="left",)

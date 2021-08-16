import pandas as pd


def join_billings_numbers(billings_numbers):
    return ", ".join(billings_numbers) if billings_numbers.apply(lambda x: not pd.isna(x)).all() else ""


def compute_billing_status(statuses: pd.Series):
    if len(statuses) == 0:
        return "awaiting_invoice"
    if statuses.isin(["new", "in_modification"]).all():
        return "awaiting_invoice"
    if statuses.isin(["due"]).any():
        return "due"
    if statuses.isin(["available"]).any():
        return "available"
    return "paid"


def add_billing_info(shipments_df: pd.DataFrame, billings_df: pd.DataFrame):
    billings_df.loc[:, "billing_numbers"] = billings_df.groupby("shipment_id")["billing_number"].transform(
        join_billings_numbers
    )
    billings_df.loc[:, "billing_status"] = billings_df.groupby("shipment_id")["status"].transform(
        compute_billing_status
    )
    billings_df = billings_df.drop_duplicates(subset=["shipment_id"])
    shipments_df = pd.merge(
        shipments_df,
        billings_df[["shipment_id", "billing_numbers", "billing_status", "billing_address_country"]],
        on="shipment_id",
        how="left",
    )
    shipments_df.loc[:, "billing_address_country"] = shipments_df.apply(
        lambda row: row["billing_address_country_y"]
        if pd.notna(row["billing_address_country_y"])
        else row["billing_address_country_x"],
        axis=1,
    )
    shipments_df = shipments_df.drop(columns=["billing_address_country_x", "billing_address_country_y"])
    shipments_df.loc[:, "billing_numbers"] = shipments_df["billing_numbers"].fillna("")
    shipments_df.loc[:, "billing_status"] = shipments_df["billing_status"].fillna("awaiting_invoice")
    return shipments_df

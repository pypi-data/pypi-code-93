import pandas as pd


def calculate_vat(prices_df: pd.DataFrame):
    return prices_df.groupby("shipment_id").sum().rename(columns={"vat_price_in_eur": "vat_price"}).reset_index()

import pandas as pd


def determine_prices_origin(prices_df: pd.DataFrame):
    return prices_df.drop_duplicates(subset=["shipment_id"])

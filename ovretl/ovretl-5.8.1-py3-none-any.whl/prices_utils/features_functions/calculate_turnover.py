import pandas as pd


def calculate_turnover(prices_df: pd.DataFrame):
    categories_to_sum = [
        "departure_truck_freight",
        "departure_fees",
        "freight",
        "arrival_fees",
        "arrival_truck_freight",
        "insurance",
    ]
    prices_df_filtered = prices_df[prices_df["category"].isin(categories_to_sum)]

    prices_df_filtered.loc[:, "turnover"] = prices_df_filtered.groupby("shipment_id")["price_in_eur"].transform(sum)
    prices_df_filtered.loc[:, "turnover_initial"] = prices_df_filtered.groupby("shipment_id")[
        "initial_price_in_eur"
    ].transform(sum)
    return prices_df_filtered.drop_duplicates("shipment_id")

import pandas as pd


def calculate_margin_without_insurance(prices_df: pd.DataFrame):
    columns_to_exclude = ["insurance", "customs", "other"]
    prices_df_without_insurance = prices_df[~prices_df["category"].isin(columns_to_exclude)]
    prices_df_without_insurance.loc[:, "margin_without_insurance"] = prices_df_without_insurance.groupby("shipment_id")[
        "margin_price_in_eur"
    ].transform(sum)
    prices_df_without_insurance.loc[:, "initial_margin_without_insurance"] = prices_df_without_insurance.groupby(
        "shipment_id"
    )["initial_margin_price_in_eur"].transform(sum)
    prices_df_without_insurance = prices_df_without_insurance.drop_duplicates("shipment_id")
    return prices_df_without_insurance


def calculate_margin_insurance(prices_df: pd.DataFrame):
    prices_df_insurance = prices_df[prices_df["category"].isin(["insurance"])]
    prices_df_insurance.loc[:, "margin_insurance"] = prices_df_insurance.groupby("shipment_id")[
        "margin_price_in_eur"
    ].transform(sum)
    prices_df_insurance.loc[:, "initial_margin_insurance"] = prices_df_insurance.groupby("shipment_id")[
        "initial_margin_price_in_eur"
    ].transform(sum)
    prices_df_insurance = prices_df_insurance.drop_duplicates("shipment_id")
    return prices_df_insurance

import pandas as pd


def pivot_shipowners_associations(shipowner_shipment_with_name_df: pd.DataFrame,) -> pd.DataFrame:
    df = pd.pivot_table(
        shipowner_shipment_with_name_df, index=["shipment_id"], columns=["role"], values=["name"], aggfunc="first",
    )
    df.columns = df.columns.droplevel()
    df = df.drop(["insurance", "other"], axis=1, errors="ignore")
    df = df.rename(
        columns={
            "arrival_fees": "arrival_shipowner",
            "arrival_truck_freight": "delivery_shipowner",
            "freight": "freight_shipowner",
            "departure_fees": "departure_shipowner",
            "departure_truck_freight": "pickup_shipowner",
        }
    )
    return df[
        ["pickup_shipowner", "departure_shipowner", "freight_shipowner", "arrival_shipowner", "delivery_shipowner",]
    ]


def add_shipowners_to_shipment(
    shipments_df: pd.DataFrame, shipowner_shipment_with_name_df: pd.DataFrame
) -> pd.DataFrame:
    shipowner_shipment_with_name_df_pivoted = pivot_shipowners_associations(shipowner_shipment_with_name_df)
    return pd.merge(
        shipments_df, shipowner_shipment_with_name_df_pivoted, left_on="shipment_id", right_index=True, how="left",
    )

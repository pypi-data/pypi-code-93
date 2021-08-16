import pandas as pd

KRONOS_ID = 125


def calculate_number_purchase_readied(activities_df: pd.DataFrame, shipments_df: pd.DataFrame):
    activities_purchase_ready_df = activities_df[
        (activities_df["header"] == "quotation_purchase_ready") & (activities_df["employee_id"] != KRONOS_ID)
    ]
    activities_purchase_ready_df = activities_purchase_ready_df.groupby("shipment_id").size()
    shipments_with_requotes = pd.merge(
        left=shipments_df,
        right=activities_purchase_ready_df.to_frame(name="nb_purchase_readied"),
        left_on="shipment_id",
        right_index=True,
        how="left",
    )
    shipments_with_requotes.loc[:, "nb_purchase_readied"] = shipments_with_requotes["nb_purchase_readied"].fillna(0)
    return shipments_with_requotes

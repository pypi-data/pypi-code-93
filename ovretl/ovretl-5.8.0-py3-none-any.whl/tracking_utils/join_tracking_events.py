import pandas as pd


def join_tracking_events(tracking_records_df: pd.DataFrame, events_df: pd.DataFrame):
    return pd.merge(
        events_df, tracking_records_df[["id", "shipment_id"]], left_on="tracking_record_id", right_on="id", how="inner",
    )

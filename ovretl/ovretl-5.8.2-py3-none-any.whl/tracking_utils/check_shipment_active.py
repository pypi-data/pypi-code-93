from datetime import datetime

import pandas as pd


def check_shipment_active(shipment: pd.Series, events_shipment_df: pd.DataFrame):
    if shipment["cancelled"] == True:
        return False
    if shipment["shipment_status"] in [
        "new",
        "not_answered",
        "propositions_sent",
        "purchase_ready",
        "to_be_requoted",
        "not_answered_declined",
    ]:
        return False
    if shipment["shipment_status"] == "finished" or not pd.isna(shipment["finished_date"]):
        return False
    shipment_events = events_shipment_df[events_shipment_df["shipment_id"] == shipment["shipment_id"]]
    if len(shipment_events) > 0 and (shipment_events["date_type"] == "actual").all():
        return False
    if (
        pd.isna(shipment["pickup_date"])
        and pd.isna(shipment["departure_date"])
        and pd.isna(shipment["arrival_date"])
        and pd.isna(shipment["delivery_date"])
    ):
        return True
    if not pd.isna(shipment["pickup_date"]) and pd.isna(shipment["departure_date"]):
        return True
    if not pd.isna(shipment["arrival_date"]) and (datetime.now() - pd.to_datetime(shipment["arrival_date"])).days > -10:
        return True
    if (
        not pd.isna(shipment["departure_date"])
        and (datetime.now() - pd.to_datetime(shipment["departure_date"])).days < 2
    ):
        return True
    return False

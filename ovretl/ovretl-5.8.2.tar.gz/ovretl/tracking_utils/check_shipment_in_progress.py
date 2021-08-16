import pandas as pd


def check_shipment_in_progress(shipment: pd.Series, events_shipment_df: pd.DataFrame) -> str:
    if shipment["shipment_status"] != "booked":
        return shipment["shipment_status"]
    shipment_events = events_shipment_df[events_shipment_df["shipment_id"] == shipment["shipment_id"]]
    if len(shipment_events) == 0:
        return "booked"
    all_events_are_done = (shipment_events["date_type"] == "actual").all()
    at_least_one_event_is_done = (shipment_events["date_type"] == "actual").any()
    if not all_events_are_done and at_least_one_event_is_done:
        return "in_progress"
    return "booked"

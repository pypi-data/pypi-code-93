import numpy as np
import pandas as pd
from ovretl.tracking_utils.check_shipment_active import check_shipment_active
from ovretl.tracking_utils.check_shipment_arrived import check_shipment_arrived
from ovretl.tracking_utils.check_shipment_in_progress import check_shipment_in_progress


def extract_event_date_by_sorting(events_shipment_df: pd.DataFrame, ascending: bool, location_key=None):
    if len(events_shipment_df) == 0:
        return np.nan
    events_shipment = events_shipment_df.sort_values(by="date", ascending=ascending).reset_index(drop=True)
    if len(events_shipment) > 0 and location_key is not None:
        if events_shipment.loc[0, "location_type"] == location_key:
            return (
                pd.to_datetime(events_shipment.loc[0, "date"])
                if not pd.isna(events_shipment.loc[0, "date"])
                else np.nan
            )
        return np.nan
    if len(events_shipment) > 0:
        return pd.to_datetime(events_shipment.loc[0, "date"]) if not pd.isna(events_shipment.loc[0, "date"]) else np.nan
    return np.nan


def extract_pickup_event_date(events_shipment_df: pd.DataFrame, date_type=None):
    mask_date_type = events_shipment_df["date_type"].apply(
        lambda event_date_type: event_date_type == date_type if date_type is not None else True
    )
    mask_etp = events_shipment_df["is_used_for_pickup"] == True
    mask_event_pickup = events_shipment_df["event_description"].apply(lambda e: "Pickup" in e)
    mask_event_not_delivery = events_shipment_df["event_description"].apply(lambda e: "Delivery" not in e)

    event_found_by_etp = extract_event_date_by_sorting(
        events_shipment_df=events_shipment_df[mask_etp & mask_date_type], ascending=True
    )
    event_found_by_description = extract_event_date_by_sorting(
        events_shipment_df=events_shipment_df[mask_event_pickup & mask_date_type], ascending=True,
    )
    event_found_by_order = extract_event_date_by_sorting(
        events_shipment_df=events_shipment_df[mask_event_not_delivery & mask_date_type],
        ascending=True,
        location_key="warehouse",
    )
    if not pd.isna(event_found_by_etp):
        return event_found_by_etp
    if not pd.isna(event_found_by_description):
        return event_found_by_description
    if not pd.isna(event_found_by_order):
        return event_found_by_order
    return np.nan


def extract_departure_event_date(events_shipment_df: pd.DataFrame, date_type=None):
    mask_date_type = events_shipment_df["date_type"].apply(
        lambda event_date_type: event_date_type == date_type if date_type is not None else True
    )
    mask_etd = events_shipment_df["is_used_for_etd"] == True
    mask_event_departure = events_shipment_df["event_description"].apply(lambda e: "Departure" in e)
    mask_event_not_arrival = events_shipment_df["event_description"].apply(lambda e: "Arrival" not in e)

    event_found_by_etd = extract_event_date_by_sorting(
        events_shipment_df=events_shipment_df[mask_etd & mask_date_type], ascending=True
    )
    event_found_by_description = extract_event_date_by_sorting(
        events_shipment_df=events_shipment_df[mask_event_departure & mask_date_type], ascending=True,
    )
    event_first = extract_event_date_by_sorting(
        events_shipment_df=events_shipment_df[mask_event_not_arrival & mask_date_type],
        ascending=True,
        location_key="harbor",
    )
    if not pd.isna(event_found_by_etd):
        return event_found_by_etd
    if not pd.isna(event_found_by_description):
        return event_found_by_description
    if not pd.isna(event_first):
        return event_first
    return np.nan


def extract_arrival_event_date(events_shipment_df: pd.DataFrame, date_type=None):
    mask_date_type = events_shipment_df["date_type"].apply(
        lambda event_date_type: event_date_type == date_type if date_type is not None else True
    )
    mask_eta = events_shipment_df["is_used_for_eta"] == True
    mask_event_arrival = events_shipment_df["event_description"].apply(lambda e: "Arrival" in e)
    mask_event_not_departure = events_shipment_df["event_description"].apply(lambda e: "Departure" not in e)

    event_found_by_eta = extract_event_date_by_sorting(
        events_shipment_df=events_shipment_df[mask_eta & mask_date_type], ascending=False,
    )
    event_found_by_description = extract_event_date_by_sorting(
        events_shipment_df=events_shipment_df[mask_event_arrival & mask_date_type], ascending=False,
    )
    event_last = extract_event_date_by_sorting(
        events_shipment_df=events_shipment_df[mask_event_not_departure & mask_date_type],
        ascending=False,
        location_key="harbor",
    )
    if not pd.isna(event_found_by_eta):
        return event_found_by_eta
    if not pd.isna(event_found_by_description):
        return event_found_by_description
    if not pd.isna(event_last):
        return event_last
    return np.nan


def extract_delivery_event_date(events_shipment_df: pd.DataFrame, date_type=None):
    mask_date_type = events_shipment_df["date_type"].apply(
        lambda event_date_type: event_date_type == date_type if date_type is not None else True
    )
    mask_etd = events_shipment_df["is_used_for_delivery"] == True
    mask_event_delivery = events_shipment_df["event_description"].apply(lambda e: "Delivery" in e)
    mask_event_not_pickup = events_shipment_df["event_description"].apply(lambda e: "Pickup" not in e)

    event_found_by_etd = extract_event_date_by_sorting(
        events_shipment_df=events_shipment_df[mask_etd & mask_date_type], ascending=False,
    )
    event_found_by_description = extract_event_date_by_sorting(
        events_shipment_df=events_shipment_df[mask_event_delivery & mask_date_type], ascending=False,
    )
    event_last = extract_event_date_by_sorting(
        events_shipment_df=events_shipment_df[mask_event_not_pickup & mask_date_type],
        ascending=False,
        location_key="warehouse",
    )
    if not pd.isna(event_found_by_etd):
        return event_found_by_etd
    if not pd.isna(event_found_by_description):
        return event_found_by_description
    if not pd.isna(event_last):
        return event_last
    return np.nan


def process_events(events_df: pd.DataFrame) -> pd.DataFrame:
    pickup_dates = events_df.groupby("shipment_id").apply(extract_pickup_event_date).rename("pickup_date")
    departure_dates = events_df.groupby("shipment_id").apply(extract_departure_event_date).rename("departure_date")
    arrival_dates = events_df.groupby("shipment_id").apply(extract_arrival_event_date).rename("arrival_date")
    delivery_dates = events_df.groupby("shipment_id").apply(extract_delivery_event_date).rename("delivery_date")
    pickup_dates_actual = (
        events_df.groupby("shipment_id")
        .apply(lambda e: extract_pickup_event_date(e, "actual"))
        .rename("actual_pickup_date")
    )
    departure_dates_actual = (
        events_df.groupby("shipment_id")
        .apply(lambda e: extract_departure_event_date(e, "actual"))
        .rename("actual_departure_date")
    )
    arrival_dates_actual = (
        events_df.groupby("shipment_id")
        .apply(lambda e: extract_arrival_event_date(e, "actual"))
        .rename("actual_arrival_date")
    )
    delivery_dates_actual = (
        events_df.groupby("shipment_id")
        .apply(lambda e: extract_delivery_event_date(e, "actual"))
        .rename("actual_delivery_date")
    )
    initial_eta_etd = events_df.drop_duplicates(subset=["shipment_id"])

    processed_dates = [
        pickup_dates,
        departure_dates,
        arrival_dates,
        delivery_dates,
        pickup_dates_actual,
        departure_dates_actual,
        arrival_dates_actual,
        delivery_dates_actual,
    ]
    events_processed_df = pd.concat(processed_dates, axis=1, keys=[s.name for s in processed_dates]).reset_index()
    return pd.merge(
        events_processed_df,
        initial_eta_etd[["shipment_id", "initial_eta", "initial_etd"]],
        on="shipment_id",
        how="left",
    )


def add_tracking_event_dates(shipments_df: pd.DataFrame, events_shipment_df: pd.DataFrame) -> pd.DataFrame:
    events_processed_df = process_events(events_df=events_shipment_df)
    shipments_df = pd.merge(shipments_df, events_processed_df, how="left", on="shipment_id")
    shipments_df.loc[:, "is_active"] = shipments_df.apply(
        lambda s: check_shipment_active(s, events_shipment_df), axis=1
    )
    shipments_df.loc[:, "shipment_status"] = shipments_df.apply(
        lambda s: check_shipment_in_progress(s, events_shipment_df), axis=1
    )
    shipments_df.loc[:, "shipment_status"] = shipments_df.apply(
        lambda s: check_shipment_arrived(s, events_shipment_df), axis=1
    )
    return shipments_df

import numpy as np
import pandas as pd
from ovretl.tracking_utils.extract_event_date import (
    extract_pickup_event_date,
    extract_arrival_event_date,
    add_tracking_event_dates,
    extract_departure_event_date,
    extract_delivery_event_date,
)
from pandas.util.testing import assert_frame_equal


def test_extract_pickup_event():
    pickup_events_shipment_df = pd.DataFrame.from_records(
        [
            {
                "shipment_id": 0,
                "event_description": "Pickup",
                "date_type": "actual",
                "date": pd.Timestamp("2020-01-02 23:00:00"),
                "location_type": "warehouse",
                "is_used_for_pickup": False,
            },
            {
                "shipment_id": 0,
                "event_description": "Pickup",
                "date_type": "estimated",
                "date": pd.Timestamp("2015-01-05 23:00:00"),
                "location_type": "warehouse",
                "is_used_for_pickup": False,
            },
        ]
    )
    pickup_date = extract_pickup_event_date(events_shipment_df=pickup_events_shipment_df, date_type=None)
    assert pickup_date == pd.Timestamp("2015-01-05 23:00:00")


def test_extract_departure_event():
    departure_events_shipment_df = pd.DataFrame.from_records(
        [
            {
                "shipment_id": 0,
                "event_description": "Pickup",
                "date_type": "estimated",
                "date": pd.Timestamp("2020-01-02 23:00:00"),
                "location_type": "warehouse",
                "is_used_for_etd": False,
            },
            {
                "shipment_id": 0,
                "event_description": "Pickup",
                "date_type": "estimated",
                "date": pd.Timestamp("2015-01-05 23:00:00"),
                "location_type": "warehouse",
                "is_used_for_etd": False,
            },
        ]
    )
    departure_date = extract_departure_event_date(events_shipment_df=departure_events_shipment_df, date_type="actual")
    assert pd.isna(departure_date)


def test_extract_arrival_event():
    arrival_events_shipment_df = pd.DataFrame.from_records(
        [
            {
                "shipment_id": 0,
                "event_description": "Arrival",
                "date_type": "actual",
                "date": pd.Timestamp("2020-01-02 23:00:00"),
                "is_used_for_eta": False,
                "location_type": "harbor",
            },
            {
                "shipment_id": 0,
                "event_description": "Arrival",
                "date_type": "estimated",
                "date": pd.Timestamp("2015-01-05 23:00:00"),
                "is_used_for_eta": True,
                "location_type": "harbor",
            },
        ]
    )
    arrival_date = extract_arrival_event_date(events_shipment_df=arrival_events_shipment_df, date_type=None)
    assert arrival_date == pd.Timestamp("2015-01-05 23:00:00")


def test_extract_delivery_event():
    delivery_events_shipment_df = pd.DataFrame.from_records(
        [
            {
                "shipment_id": 0,
                "event_description": "Delivery",
                "date_type": "actual",
                "date": pd.Timestamp("2020-01-02 23:00:00"),
                "location_type": "warehouse",
                "is_used_for_delivery": False,
            },
            {
                "shipment_id": 0,
                "event_description": "Delivery",
                "date_type": "estimated",
                "date": pd.Timestamp("2025-01-05 23:00:00"),
                "location_type": "warehouse",
                "is_used_for_delivery": False,
            },
        ]
    )
    delivery_date = extract_delivery_event_date(events_shipment_df=delivery_events_shipment_df, date_type="estimated")
    assert delivery_date == pd.Timestamp("2025-01-05 23:00:00")


def test_add_tracking_events():
    events_shipment_df = pd.DataFrame.from_records(
        [
            {
                "shipment_id": 0,
                "event_description": "Pickup",
                "date_type": "estimated",
                "date": pd.Timestamp("2020-01-02 23:00:00"),
                "location_type": "warehouse",
                "is_used_for_etd": False,
                "is_used_for_eta": False,
                "is_used_for_pickup": False,
                "is_used_for_delivery": False,
                "initial_eta": np.nan,
                "initial_etd": np.nan,
                "initial_pickup_date": np.nan,
                "initial_delivery_date": np.nan,
            },
            {
                "shipment_id": 0,
                "event_description": "Pickup",
                "date_type": "estimated",
                "date": pd.Timestamp("2015-01-05 23:00:00"),
                "location_type": "warehouse",
                "is_used_for_etd": False,
                "is_used_for_eta": False,
                "is_used_for_pickup": False,
                "is_used_for_delivery": False,
                "initial_eta": np.nan,
                "initial_etd": np.nan,
                "initial_pickup_date": np.nan,
                "initial_delivery_date": np.nan,
            },
        ]
    )
    shipments_df = pd.DataFrame(
        data={"shipment_id": [0], "cancelled": [False], "shipment_status": ["booked"], "finished_date": [np.nan],}
    )
    result = add_tracking_event_dates(shipments_df, events_shipment_df)
    result_should_be = pd.DataFrame(
        data={
            "shipment_id": [0],
            "cancelled": [False],
            "shipment_status": ["booked"],
            "finished_date": [np.nan],
            "pickup_date": [pd.Timestamp("2015-01-05 23:00:00")],
            "departure_date": [np.nan],
            "arrival_date": [np.nan],
            "delivery_date": [np.nan],
            "actual_pickup_date": [np.nan],
            "actual_departure_date": [np.nan],
            "actual_arrival_date": [np.nan],
            "actual_delivery_date": [np.nan],
            "initial_eta": [np.nan],
            "initial_etd": [np.nan],
            "is_active": [True],
        }
    )
    assert_frame_equal(result, result_should_be)

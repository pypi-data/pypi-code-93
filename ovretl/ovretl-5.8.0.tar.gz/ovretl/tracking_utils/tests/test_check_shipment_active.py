from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from ovretl.tracking_utils.check_shipment_active import check_shipment_active

empty_events_df = pd.DataFrame(data={"shipment_id": []})


def test_check_shipment_active():
    quotation = pd.Series(data=["0", "to_be_requoted", False], index=["shipment_id", "shipment_status", "cancelled"],)
    assert not check_shipment_active(quotation, empty_events_df)
    finished = pd.Series(data=["0", "finished", False], index=["shipment_id", "shipment_status", "cancelled"],)
    assert not check_shipment_active(finished, empty_events_df)
    arrival_date_active = pd.Series(
        data=["0", "in_progress", np.nan, np.nan, np.nan, datetime.now() + timedelta(days=5), np.nan, False,],
        index=[
            "shipment_id",
            "shipment_status",
            "finished_date",
            "pickup_date",
            "departure_date",
            "arrival_date",
            "delivery_date",
            "cancelled",
        ],
    )
    assert check_shipment_active(arrival_date_active, empty_events_df)
    arrival_date_not_active = pd.Series(
        data=["0", "booking_request", np.nan, np.nan, np.nan, datetime.now() + timedelta(days=11), np.nan, False,],
        index=[
            "shipment_id",
            "shipment_status",
            "finished_date",
            "pickup_date",
            "departure_date",
            "arrival_date",
            "delivery_date",
            "cancelled",
        ],
    )
    assert not check_shipment_active(arrival_date_not_active, empty_events_df)
    departure_date_active = pd.Series(
        data=["0", "in_progress", np.nan, np.nan, datetime.now() - timedelta(days=1), np.nan, np.nan, False,],
        index=[
            "shipment_id",
            "shipment_status",
            "finished_date",
            "pickup_date",
            "departure_date",
            "arrival_date",
            "delivery_date",
            "cancelled",
        ],
    )
    assert check_shipment_active(departure_date_active, empty_events_df)
    departure_date_not_active = pd.Series(
        data=["0", "in_progress", np.nan, np.nan, datetime.now() - timedelta(days=5), np.nan, np.nan, False,],
        index=[
            "shipment_id",
            "shipment_status",
            "finished_date",
            "pickup_date",
            "departure_date",
            "arrival_date",
            "delivery_date",
            "cancelled",
        ],
    )
    assert not check_shipment_active(departure_date_not_active, empty_events_df)
    is_arrived = pd.Series(
        data=["0", "in_progress", np.nan, np.nan, datetime.now() - timedelta(days=1), np.nan, np.nan, False,],
        index=[
            "shipment_id",
            "shipment_status",
            "finished_date",
            "pickup_date",
            "departure_date",
            "arrival_date",
            "delivery_date",
            "cancelled",
        ],
    )
    assert not check_shipment_active(
        is_arrived, pd.DataFrame(data={"shipment_id": ["0", "0"], "date_type": ["actual", "actual"]}),
    )
    is_not_arrived_and_active = pd.Series(
        data=["0", "in_progress", np.nan, np.nan, datetime.now() - timedelta(days=1), np.nan, np.nan, False,],
        index=[
            "shipment_id",
            "shipment_status",
            "finished_date",
            "pickup_date",
            "departure_date",
            "arrival_date",
            "delivery_date",
            "cancelled",
        ],
    )
    assert check_shipment_active(
        is_not_arrived_and_active, pd.DataFrame(data={"shipment_id": ["0", "0"], "date_type": ["actual", "estimated"]}),
    )

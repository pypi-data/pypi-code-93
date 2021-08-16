from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from ovretl.tracking_utils.check_shipment_in_progress import check_shipment_in_progress

empty_events_df = pd.DataFrame(data={"shipment_id": []})


def test_check_shipment_in_progress():
    quotation = pd.Series(data=["0", "to_be_requoted", False], index=["shipment_id", "shipment_status", "cancelled"],)
    assert check_shipment_in_progress(quotation, empty_events_df) == "to_be_requoted"
    finished = pd.Series(data=["0", "booked", False], index=["shipment_id", "shipment_status", "cancelled"],)
    assert check_shipment_in_progress(finished, empty_events_df) == "booked"

    is_arrived = pd.Series(
        data=["0", "booked", np.nan, np.nan, datetime.now() - timedelta(days=1), np.nan, np.nan, False,],
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
    assert (
        check_shipment_in_progress(
            is_arrived, pd.DataFrame(data={"shipment_id": ["0", "0"], "date_type": ["actual", "actual"]}),
        )
        == "booked"
    )
    is_not_arrived_and_active = pd.Series(
        data=["0", "booked", np.nan, np.nan, datetime.now() - timedelta(days=1), np.nan, np.nan, False,],
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
    assert (
        check_shipment_in_progress(
            is_not_arrived_and_active,
            pd.DataFrame(data={"shipment_id": ["0", "0"], "date_type": ["actual", "estimated"]}),
        )
        == "in_progress"
    )

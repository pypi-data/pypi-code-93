import pandas as pd

from ovretl.shipments_utils.shipment_with_total_transit_time import shipments_with_total_transit_time


def test_shipments_accepted_proposition_total_transit_time():
    sh_df = pd.DataFrame(
        data={
            "shipment_id": ["1", "2", "3", "4"],
            "shipment_status": ["booked", "awaiting_booking", "finished", "booked"],
            "proposition_status": ["accepted", "sent", "accepted", "accepted"],
            "cancelled": [False, False, False, True],
            "transit_time_door_to_port": 1,
            "transit_time": 2,
            "transit_time_port_to_door": 3,
        }
    )
    result_should_be = sh_df[sh_df["shipment_id"].isin(["1", "2"])]
    result_should_be["total_transit_time"] = 6
    result = shipments_with_total_transit_time(sh_df)
    pd.testing.assert_frame_equal(result, result_should_be)

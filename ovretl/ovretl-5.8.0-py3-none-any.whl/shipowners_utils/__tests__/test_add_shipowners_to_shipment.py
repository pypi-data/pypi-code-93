import numpy as np
import pandas as pd
from ovretl import add_shipowners_to_shipment
from pandas.util.testing import assert_frame_equal


def test_add_shipowners_to_shipment():
    shipowners_asociations = pd.DataFrame(
        data={
            "shipment_id": [1, 1, 1, 1, 1, 3, 3],
            "role": [
                "departure_truck_freight",
                "departure_fees",
                "freight",
                "arrival_fees",
                "arrival_truck_freight",
                "freight",
                "departure_truck_freight",
            ],
            "name": ["MSC", "Morrisson", "MSC", "Fatton", "MSC", "Air France", "Everoad",],
        }
    )
    shipments_df = pd.DataFrame(data={"shipment_id": [1, 2],})
    result = add_shipowners_to_shipment(shipments_df, shipowners_asociations)
    result_should_be = pd.DataFrame(
        data={
            "shipment_id": [1, 2],
            "pickup_shipowner": ["MSC", np.nan],
            "departure_shipowner": ["Morrisson", np.nan],
            "freight_shipowner": ["MSC", np.nan],
            "arrival_shipowner": ["Fatton", np.nan],
            "delivery_shipowner": ["MSC", np.nan],
        }
    )
    assert_frame_equal(result, result_should_be)

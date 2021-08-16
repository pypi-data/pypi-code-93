import pandas as pd
from pandas.util.testing import assert_frame_equal

from ovretl.performances_utils.calculate_number_purchase_readied import calculate_number_purchase_readied


def test_calculate_number_purchase_readied():
    activities_df = pd.DataFrame(
        data={
            "shipment_id": [0, 0, 1, 1],
            "employee_id": [0, 1, 2, 3],
            "header": ["quotation_purchase_ready", "quotation_purchase_ready", "quotation_purchase_ready", "bar"],
        }
    )
    shipments_df = pd.DataFrame(data={"shipment_id": [0, 1, 2]})
    result = calculate_number_purchase_readied(activities_df=activities_df, shipments_df=shipments_df)
    result_should_be = pd.DataFrame(data={"shipment_id": [0, 1, 2], "nb_purchase_readied": [2, 1, 0]})
    assert_frame_equal(result, result_should_be, check_dtype=False)

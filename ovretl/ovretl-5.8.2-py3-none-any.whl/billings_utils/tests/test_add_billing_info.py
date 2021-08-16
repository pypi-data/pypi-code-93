import numpy as np
import pandas as pd
from ovretl import add_billing_info
from pandas.util.testing import assert_frame_equal


def test_add_billing_info():
    billings_df = pd.DataFrame(
        data={
            "shipment_id": ["0", "0", "1", "1", "2", "2", "4"],
            "billing_number": ["ABC", "DEF", "GHI", np.nan, np.nan, np.nan, "JKL"],
            "billing_address_country": ["fr", "cn", "uk", np.nan, np.nan, np.nan, "fr"],
            "status": ["new", "in_modification", "due", "in_modification", "paid", "in_modification", "paid",],
        }
    )
    shipments_df = pd.DataFrame(
        data={"shipment_id": ["0", "1", "2", "3"], "billing_address_country": ["us", np.nan, np.nan, "be"]}
    )
    result = add_billing_info(shipments_df=shipments_df, billings_df=billings_df)
    result_should_be = pd.DataFrame(
        data={
            "shipment_id": ["0", "1", "2", "3"],
            "billing_numbers": ["ABC, DEF", "", "", ""],
            "billing_status": ["awaiting_invoice", "due", "paid", "awaiting_invoice"],
            "billing_address_country": ["fr", "uk", np.nan, "be"],
        }
    )
    assert_frame_equal(result, result_should_be)

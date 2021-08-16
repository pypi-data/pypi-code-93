import numpy as np
import pandas as pd
from ovretl.loads_utils.merge_shipments_with_loads import (
    split_propositions_shipments_loads,
    merge_with_propositions_loads_then_with_shipments_loads,
)
from pandas.util.testing import assert_frame_equal

pd.set_option("display.max_columns", None)


def test_merge_with_propositions_loads_then_with_shipments_loads():
    loads_df = pd.DataFrame(
        data={
            "total_number": [1, 2, 1, 1],
            "total_weight": [200, 100, 200, 200],
            "total_volume": [0.9, 0.9, 1, 0.96],
            "shipment_id": [np.nan, np.nan, "2", "3"],
            "proposition_id": ["0", "1", np.nan, np.nan],
            "taxable_weight": [200, 150, 200, 200],
            "weight_measurable": [1, 1, 1, 1],
            "hazardous": [True, True, False, False],
            "non_stackable": [True, False, False, False],
            "magnetic": [False, False, False, False],
            "refrigerated": [False, False, False, False],
            "lithium": [False, False, False, False],
        }
    )
    shipments_df = pd.DataFrame(data={"shipment_id": [np.nan, "2", "3"], "proposition_id": ["0", "1", np.nan]})
    result_should_be = pd.DataFrame(
        data={
            "shipment_id": [np.nan, "2", "3"],
            "proposition_id": ["0", "1", np.nan],
            "total_number": [1, 2, 1],
            "total_volume": [0.9, 0.9, 0.96],
            "total_weight": [200, 100, 200],
            "taxable_weight": [200, 150, 200],
            "weight_measurable": [1, 1, 1],
            "loads_hazardous": [True, True, False],
            "loads_lithium": [False, False, False],
            "non_stackable": [True, False, False],
            "loads_magnetic": [np.nan, np.nan, False],
            "loads_refrigerated": [np.nan, np.nan, False],
        }
    )
    (propositions_loads_df, shipments_loads_df,) = split_propositions_shipments_loads(loads_df)

    result = merge_with_propositions_loads_then_with_shipments_loads(
        shipments_df=shipments_df, propositions_loads_df=propositions_loads_df, shipments_loads_df=shipments_loads_df,
    )
    assert_frame_equal(result, result_should_be, check_dtype=False)

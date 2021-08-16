import numpy as np
import pandas as pd
from ovretl.loads_utils.calculate_entity_loads import calculate_shipments_propositions_loads
from pandas.util.testing import assert_frame_equal


def test_calculate_entity_loads():
    loads_df = pd.DataFrame(
        data={
            "unit_weight": [10, 0, 100, 10, 10],
            "unit_length": [120, 0, 120, 120, 120],
            "unit_height": [100, 0, 100, 100, 100],
            "unit_width": [80, 0, 80, 80, 80],
            "unit_number": [1, 0, 1, 1, 1],
            "total_weight": [200, 0, np.nan, 200, 200],
            "total_volume": [0.9, 0, 0.9, 1, np.nan],
            "proposition_id": ["0", "0", "1", np.nan, np.nan],
            "shipment_id": [np.nan, np.nan, np.nan, "2", "3"],
            "hazardous": [True, True, True, False, False],
            "non_stackable": [False, True, False, False, False],
            "magnetic": [False, False, False, False, False],
            "refrigerated": [False, False, False, False, False],
            "lithium": [False, False, False, False, False],
        }
    )
    result_should_be = pd.DataFrame(
        data={
            "total_weight": [200, 100, 200, 200],
            "total_volume": [0.9, 0.9, 1, 0.96],
            "total_number": [1, 1, 1, 1],
            "proposition_id": ["0", "1", np.nan, np.nan],
            "shipment_id": [np.nan, np.nan, "2", "3"],
            "taxable_weight": [200, 150, 200, 200],
            "weight_measurable": [1, 1, 1, 1],
            "hazardous": [True, True, False, False],
            "non_stackable": [True, False, False, False],
            "magnetic": [False, False, False, False],
            "refrigerated": [False, False, False, False],
            "lithium": [False, False, False, False],
        }
    )
    result = calculate_shipments_propositions_loads(loads_df).reset_index(drop=True)
    assert_frame_equal(result, result_should_be, check_dtype=False, check_like=True)

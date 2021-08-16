import numpy as np
import pandas as pd
from ovretl.loads_utils.calculate_single_load_total_quantities import calculate_single_load_total_quantities
from pandas.util.testing import assert_frame_equal


def test_calculate_single_loads_total_quantities():
    loads_df = pd.DataFrame(
        data={
            "unit_weight": [10, 100, 10, 10],
            "unit_length": [120, 120, 120, 120],
            "unit_height": [100, 100, 100, 100],
            "unit_width": [80, 80, 80, 80],
            "unit_number": [1, 1, 1, 1],
            "total_weight": [200, np.nan, 200, 200],
            "total_volume": [0.9, 0.9, 1, np.nan],
        }
    )
    loads_df_with_total_quantities = pd.DataFrame(
        data={
            "unit_weight": [10, 100, 10, 10],
            "unit_length": [120, 120, 120, 120],
            "unit_height": [100, 100, 100, 100],
            "unit_width": [80, 80, 80, 80],
            "unit_number": [1, 1, 1, 1],
            "total_weight": [200, 100, 200, 200],
            "total_volume": [0.9, 0.9, 1, 0.96],
            "total_number": [1, 1, 1, 1],
        }
    )
    loads_df = loads_df.apply(calculate_single_load_total_quantities, axis=1)
    assert_frame_equal(loads_df, loads_df_with_total_quantities, check_dtype=False)

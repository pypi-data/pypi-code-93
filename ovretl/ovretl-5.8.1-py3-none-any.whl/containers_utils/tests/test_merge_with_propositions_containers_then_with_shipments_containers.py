import numpy as np
import pandas as pd
from ovretl.containers_utils.merge_shipments_with_containers import (
    split_propositions_shipments_containers,
    merge_with_propositions_containers_then_with_shipments_containers,
)
from pandas.util.testing import assert_frame_equal


def test_merge_with_propositions_containers_then_with_shipments_containers():
    containers_df = pd.DataFrame(
        data={
            "teus": [4, 1, 2, 2],
            "tc": [1, 1, 1, 1],
            "shipment_id": [np.nan, np.nan, "2", "3"],
            "proposition_id": ["0", "1", np.nan, np.nan],
            "hazardous": [True, True, False, False],
            "refrigerated": [False, False, True, True],
        }
    )
    shipments_df = pd.DataFrame(data={"shipment_id": [np.nan, "2", "3"], "proposition_id": ["0", "1", np.nan]})
    shipments_df_true = pd.DataFrame(
        data={
            "shipment_id": [np.nan, "2", "3"],
            "proposition_id": ["0", "1", np.nan],
            "teus": [4, 1, 2],
            "tc": [1, 1, 1],
            "containers_hazardous": [True, True, False],
            "containers_refrigerated": [False, False, True],
        }
    )
    (propositions_containers_df, shipments_containers_df,) = split_propositions_shipments_containers(containers_df)

    shipments_df_processed = merge_with_propositions_containers_then_with_shipments_containers(
        shipments_df=shipments_df,
        propositions_containers_df=propositions_containers_df,
        shipments_containers_df=shipments_containers_df,
    )
    assert_frame_equal(shipments_df_processed, shipments_df_true, check_dtype=False)

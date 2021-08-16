import numpy as np
import pandas as pd

from ovretl import match_kronos_propositions_and_shipments


def test_match_kronos_propositions_and_shipments():
    kronos_propositions_df = pd.DataFrame(
        data={
            "id": [1, 2, 3, 4, 5, 6],
            "shipment_id": [0, 0, 1, 1, 2, 4],
            "proposition_id": [1, np.nan, 5, np.nan, np.nan, np.nan],
            "created_at": [1, 2, 3, 4, 6, 5],
        }
    )
    shipments_with_proposition_df = pd.DataFrame(
        data={
            "id": [1, 2, 3, 4, 10],
            "proposition_id": [1, 2, 3, 4, np.nan],
            "kronos_action": [np.nan, np.nan, "set_proposition_purchase_ready", "set_proposition_purchase_ready",
                              "set_proposition_purchase_ready"],
            "foresea_name": ["BATD", np.nan, "BATE", "BATF", "BATG"],
            "kronos_proposition_id": [np.nan, 100, 101, 6, 103],
        }
    )
    result_should_be = pd.DataFrame(
        data={
            "kronos_proposition_id": [6, 5, 3, 1],
            "shipment_id": [4, 2, 1, 0],
            "created_at": [5, 6, 3, 1],
            "proposition_id": [4, np.nan, 5, 1],
            "kronos_action": ["set_proposition_purchase_ready", np.nan, np.nan, np.nan],
        }
    )
    result = match_kronos_propositions_and_shipments(kronos_propositions_df, shipments_with_proposition_df)
    pd.testing.assert_frame_equal(result.reset_index(drop=True), result_should_be.reset_index(drop=True))

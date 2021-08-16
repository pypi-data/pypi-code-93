import numpy as np
import pandas as pd

from ovretl.shipment_orchestration_utils.so_workflows_weights import so_workflows_weights


def test_so_workflows_weights():

    wf_df = pd.DataFrame(data={"id": ["1", "2", "3"], "name": ["wf1", "wf2", "wf3"],})
    st_df = pd.DataFrame(data={"id": ["1", "2", "3", "4"], "so_workflow_id": ["1", "2", "3", "3"],})
    sa_assoc_df = pd.DataFrame(
        data={
            "id": ["1", "2", "3", "4", "5"],
            "so_state_id": ["1", "2", "2", "3", "4"],
            "so_action_id": ["1", "2", "3", "4", "5"],
        }
    )
    ac_df = pd.DataFrame(data={"id": ["1", "2", "3", "4", "5"], "weight": [1, 1, 1, 1, 1],})
    result_should_be = pd.DataFrame(
        data={"id": ["1", "2", "3"], "name": ["wf1", "wf2", "wf3"], "total_workflow_weight": [1, 2, 2]}
    )

    result = so_workflows_weights(wf_df, st_df, sa_assoc_df, ac_df)
    pd.testing.assert_frame_equal(result, result_should_be)

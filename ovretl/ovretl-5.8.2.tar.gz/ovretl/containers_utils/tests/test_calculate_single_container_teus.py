import pandas as pd

from pandas.util.testing import assert_frame_equal
from ovretl.containers_utils.calculate_single_container_teus import calculate_single_container_teus


def test_calculate_single_container_teus():
    containers_df = pd.DataFrame(data={"container_type": ["twenty_standard", "fortyfive_highcube"]})
    containers_df_with_teus = pd.DataFrame(
        data={"container_type": ["twenty_standard", "fortyfive_highcube"], "teus": [1, 2],}
    )
    containers_df = containers_df.apply(calculate_single_container_teus, axis=1)
    assert_frame_equal(containers_df, containers_df_with_teus, check_dtype=False)

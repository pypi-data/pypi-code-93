import os
import pandas as pd
import numpy as np
from numpy.testing import assert_array_almost_equal

from bridget import sap_flow

DATA = os.path.join(os.path.dirname(__file__), '../../data')


def get_data(use_velocity=False):
    if use_velocity:
        path = os.path.join(DATA, 'Vsap_M_A_Sapflow_korr.dat.txt')
    else:
        path = os.path.join(DATA, 'M_A_Sapflow_korr.dat')
    
    #read data
    df = pd.read_csv(path, delimiter='\s+')

    return df


def test_calculate_velocity():
    # get the data
    df = get_data(use_velocity=False)

    result = sap_flow.sap_velocity_heat_ratio(df.iloc[:100, 30:33].values, df.iloc[:100, 34:37].values)

    # test result dimensions
    assert len(result.shape) == 2
    assert result.shape[0] == 100 and result.shape[1] == 3

    # test result
    assert_array_almost_equal(
        result,
        np.random.normal(0, 1, size=(100,3)),
        decimal=2
    )

if __name__ == '__main__':
    test_calculate_velocity()
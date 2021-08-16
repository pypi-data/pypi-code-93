import pandas as pd
import pytest
from saxton2006 import pth_clean
from saxton2006.table1 import theta_1500, theta_33, theta_sat, water_conductance_sat


def test_pedotransfer_matches_table3():
    # read table3
    df = pd.read_csv(pth_clean / "table3.csv", sep=";", comment="#", index_col=['texture'])
    om = 2.5 / 100
    for cname in ('clay', 'sand', 'theta_fc', 'theta_pwp', 'theta_sat'):
        df[cname] /= 100

    # perform line by line comparison
    for tex, row in df.iterrows():
        assert theta_1500(row['clay'], row['sand'], om) == pytest.approx(row['theta_pwp'], abs=0.5)
        assert theta_33(row['clay'], row['sand'], om) == pytest.approx(row['theta_fc'], abs=0.5)
        assert theta_sat(row['clay'], row['sand'], om) == pytest.approx(row['theta_sat'], abs=0.5)
        th_1500 = theta_1500(row['clay'], row['sand'], om)
        th_33 = theta_33(row['clay'], row['sand'], om)
        th_sat = theta_sat(row['clay'], row['sand'], om)
        assert water_conductance_sat(th_sat, th_33, th_1500) == pytest.approx(row['k_sat'], abs=0.5)

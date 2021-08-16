import pandas as pd
import numpy as np


from pandas.util.testing import assert_frame_equal
from ovretl.employees_utils.find_shipment_employee_name import add_employees_to_shipments


def test_add_employees_to_shipments():
    shipments_df = pd.DataFrame(data={"sales_owner_id": [1], "operations_owner_id": [np.nan], "pricing_owner_id": [3],})
    employees_df = pd.DataFrame(data={"id": [1, 2, 3], "name": ["Gautier", "Oria", "Jean"]})
    result = add_employees_to_shipments(shipments_df, employees_df)
    result_should_be = pd.DataFrame(data={"sales": ["Gautier"], "operations": [np.nan], "pricing": ["Jean"],})
    assert_frame_equal(result, result_should_be, check_dtype=False)

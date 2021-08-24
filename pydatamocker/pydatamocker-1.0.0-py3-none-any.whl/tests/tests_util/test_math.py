import pytest
from pydatamocker.util.math import round


def test_rounding():
    decimals = 3
    numbers = round([2, 3.3, -2.2315151235, -3.21, 1095521.22, 23341.0, 3231.090521], decimals)
    for num in numbers:
        str_num = str(num)
        pt_index = str_num.find('.')
        str_num = str_num[pt_index + 1:]
        assert decimals >= len(str_num), 'Rounded incorrectly. Should be at most 3 decimal places'

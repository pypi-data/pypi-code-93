import logging
import random

import numpy as np
import pytest

from dkist_processing_common.parsers.cs_step import CSStep


def test_equal_correct(grouped_cal_sequence_headers):
    """
    Given: A set of PolCal headers
    When: Converting them to CSStep objects and comparing them
    Then: All headers belonging to the same step produce CSStep objects that are equal
    """
    for cs_header_list in grouped_cal_sequence_headers.values():
        for i in range(len(cs_header_list)):
            assert CSStep(cs_header_list[0]) == CSStep(cs_header_list[i])


@pytest.mark.parametrize("stepnum", [pytest.param(i, id=f"step {i}") for i in range(7)])
def test_not_equal_correct(grouped_cal_sequence_headers, stepnum):
    """
    Given: A set of PolCal headers
    When: Converting them to CSStep objects and comparing them
    Then: All objects from a single step are not equal to all objects from other steps
    """
    for i in range(7):
        if i != stepnum:
            assert CSStep(grouped_cal_sequence_headers[stepnum][0]) != CSStep(
                grouped_cal_sequence_headers[i][0]
            )


def test_not_equal_non_CS_Step_type(grouped_cal_sequence_headers):
    """
    Given: A PolCal header and resulting CSStep object
    When: Testing equality with a non CSStep object
    Then: An error is raised
    """
    cs_step = CSStep(grouped_cal_sequence_headers[0][0])
    with pytest.raises(TypeError):
        _ = cs_step == 1


def test_order_correct(grouped_cal_sequence_headers):
    """
    Given: A set of PolCal headers
    When: Converting them to CSStep objects and ordering them
    Then: The step objects are correctly ordered by observe time
    """
    logging.warning(f"{grouped_cal_sequence_headers}")
    cs_step_list = [CSStep(header) for header in sum(grouped_cal_sequence_headers.values(), [])]
    random.shuffle(cs_step_list)  # Just to mix it up a bit
    time_list = [c.obs_time for c in cs_step_list]
    cs_sort_idx = np.argsort(cs_step_list)
    time_sort_idx = np.argsort(time_list)
    assert np.array_equal(cs_sort_idx, time_sort_idx)

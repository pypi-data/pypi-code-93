import numpy as np
import pytest

import pandas as pd
import pandas._testing as tm


@pytest.mark.parametrize("align_axis", [0, 1, "index", "columns"])
def test_compare_axis(align_axis):
    # GH#30429
    s1 = pd.Series(["a", "b", "c"])
    s2 = pd.Series(["x", "b", "z"])

    result = s1.compare(s2, align_axis=align_axis)

    if align_axis in (1, "columns"):
        indices = pd.Index([0, 2])
        columns = pd.Index(["self", "other"])
        expected = pd.DataFrame(
            [["a", "x"], ["c", "z"]], index=indices, columns=columns
        )
        tm.assert_frame_equal(result, expected)
    else:
        indices = pd.MultiIndex.from_product([[0, 2], ["self", "other"]])
        expected = pd.Series(["a", "x", "c", "z"], index=indices)
        tm.assert_series_equal(result, expected)


@pytest.mark.parametrize(
    "keep_shape, keep_equal",
    [
        (True, False),
        (False, True),
        (True, True),
        # False, False case is already covered in test_compare_axis
    ],
)
def test_compare_various_formats(keep_shape, keep_equal):
    s1 = pd.Series(["a", "b", "c"])
    s2 = pd.Series(["x", "b", "z"])

    result = s1.compare(s2, keep_shape=keep_shape, keep_equal=keep_equal)

    if keep_shape:
        indices = pd.Index([0, 1, 2])
        columns = pd.Index(["self", "other"])
        if keep_equal:
            expected = pd.DataFrame(
                [["a", "x"], ["b", "b"], ["c", "z"]], index=indices, columns=columns
            )
        else:
            expected = pd.DataFrame(
                [["a", "x"], [np.nan, np.nan], ["c", "z"]],
                index=indices,
                columns=columns,
            )
    else:
        indices = pd.Index([0, 2])
        columns = pd.Index(["self", "other"])
        expected = pd.DataFrame(
            [["a", "x"], ["c", "z"]], index=indices, columns=columns
        )
    tm.assert_frame_equal(result, expected)


def test_compare_with_equal_nulls():
    # We want to make sure two NaNs are considered the same
    # and dropped where applicable
    s1 = pd.Series(["a", "b", np.nan])
    s2 = pd.Series(["x", "b", np.nan])

    result = s1.compare(s2)
    expected = pd.DataFrame([["a", "x"]], columns=["self", "other"])
    tm.assert_frame_equal(result, expected)


def test_compare_with_non_equal_nulls():
    # We want to make sure the relevant NaNs do not get dropped
    s1 = pd.Series(["a", "b", "c"])
    s2 = pd.Series(["x", "b", np.nan])

    result = s1.compare(s2, align_axis=0)

    indices = pd.MultiIndex.from_product([[0, 2], ["self", "other"]])
    expected = pd.Series(["a", "x", "c", np.nan], index=indices)
    tm.assert_series_equal(result, expected)


def test_compare_multi_index():
    index = pd.MultiIndex.from_arrays([[0, 0, 1], [0, 1, 2]])
    s1 = pd.Series(["a", "b", "c"], index=index)
    s2 = pd.Series(["x", "b", "z"], index=index)

    result = s1.compare(s2, align_axis=0)

    indices = pd.MultiIndex.from_arrays(
        [[0, 0, 1, 1], [0, 0, 2, 2], ["self", "other", "self", "other"]]
    )
    expected = pd.Series(["a", "x", "c", "z"], index=indices)
    tm.assert_series_equal(result, expected)


def test_compare_unaligned_objects():
    # test Series with different indices
    msg = "Can only compare identically-labeled Series objects"
    with pytest.raises(ValueError, match=msg):
        ser1 = pd.Series([1, 2, 3], index=["a", "b", "c"])
        ser2 = pd.Series([1, 2, 3], index=["a", "b", "d"])
        ser1.compare(ser2)

    # test Series with different lengths
    msg = "Can only compare identically-labeled Series objects"
    with pytest.raises(ValueError, match=msg):
        ser1 = pd.Series([1, 2, 3])
        ser2 = pd.Series([1, 2, 3, 4])
        ser1.compare(ser2)

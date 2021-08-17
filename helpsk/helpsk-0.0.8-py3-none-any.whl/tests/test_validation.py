import unittest
from datetime import timedelta

import numpy as np
import pandas as pd

from helpsk import string as hs
from helpsk import validation as hv


# noinspection PyMethodMayBeStatic
class TestValidation(unittest.TestCase):

    def test_any_none_nan(self):
        assert hv.any_none_nan(None)  # noqa
        assert hv.any_none_nan(np.NaN)

        # test list
        assert hv.any_none_nan([1, np.nan, None])
        assert hv.any_none_nan([1, np.nan])
        assert hv.any_none_nan([1, None])
        assert hv.any_none_nan([np.nan])
        assert hv.any_none_nan([None])
        assert hv.any_none_nan([])
        assert not hv.any_none_nan([1])
        assert not hv.any_none_nan([''])

        # test numpy array
        assert hv.any_none_nan(np.array([1, np.nan, None]))
        assert hv.any_none_nan(np.array([1, np.nan]))
        assert hv.any_none_nan(np.array([1, None]))
        assert hv.any_none_nan(np.array([np.nan]))
        assert hv.any_none_nan(np.array([None]))
        assert hv.any_none_nan(np.array([]))
        assert not hv.any_none_nan(np.array([1]))
        assert not hv.any_none_nan(np.array(['']))

        # test pandas series
        assert hv.any_none_nan(pd.Series([1, np.nan, None]))
        assert hv.any_none_nan(pd.Series([1, np.nan]))
        assert hv.any_none_nan(pd.Series([1, None]))
        assert hv.any_none_nan(pd.Series([np.nan]))
        assert hv.any_none_nan(pd.Series([None]))
        assert hv.any_none_nan(pd.Series([], dtype=float))
        assert not hv.any_none_nan(pd.Series([1]))
        assert not hv.any_none_nan(pd.Series(['']))

        # test pandas data.frame
        assert hv.any_none_nan(pd.DataFrame([[1, np.nan, None], [1, 2, 3]]))
        assert hv.any_none_nan(pd.DataFrame([[1, np.nan], [1, 2]]))
        assert hv.any_none_nan(pd.DataFrame([[1, None], [1, 2]]))
        assert hv.any_none_nan(pd.DataFrame([[np.nan], [1]]))
        assert hv.any_none_nan(pd.DataFrame([[None], [1]]))
        assert hv.any_none_nan(pd.DataFrame([], dtype=float))
        assert not hv.any_none_nan(pd.DataFrame([1]))
        assert not hv.any_none_nan(pd.DataFrame([[1], [1]]))
        assert not hv.any_none_nan(pd.DataFrame([[''], [1]]))

    def test_assert_not_none_nan(self):
        assert hv.raises_exception(lambda: hv.assert_not_none_nan(None),  # noqa
                                   AssertionError)
        assert hv.raises_exception(lambda: hv.assert_not_none_nan(np.NaN),
                                   AssertionError)

        # test list
        assert hv.raises_exception(lambda: hv.assert_not_none_nan([1, np.nan, None]),
                                   AssertionError)
        assert hv.raises_exception(lambda: hv.assert_not_none_nan([1, np.nan]),
                                   AssertionError)
        assert hv.raises_exception(lambda: hv.assert_not_none_nan([1, None]),
                                   AssertionError)
        assert hv.raises_exception(lambda: hv.assert_not_none_nan([np.nan]),
                                   AssertionError)
        assert hv.raises_exception(lambda: hv.assert_not_none_nan([None]),
                                   AssertionError)
        assert hv.raises_exception(lambda: hv.assert_not_none_nan([]),
                                   AssertionError)
        assert not hv.raises_exception(lambda: hv.assert_not_none_nan([1]))
        assert not hv.raises_exception(lambda: hv.assert_not_none_nan(['']))

        # test numpy array
        assert hv.raises_exception(lambda: hv.assert_not_none_nan(np.array([1, np.nan, None])),
                                   AssertionError)
        assert hv.raises_exception(lambda: hv.assert_not_none_nan(np.array([1, np.nan])),
                                   AssertionError)
        assert hv.raises_exception(lambda: hv.assert_not_none_nan(np.array([1, None])),
                                   AssertionError)
        assert hv.raises_exception(lambda: hv.assert_not_none_nan(np.array([np.nan])),
                                   AssertionError)
        assert hv.raises_exception(lambda: hv.assert_not_none_nan(np.array([None])),
                                   AssertionError)
        assert hv.raises_exception(lambda: hv.assert_not_none_nan(np.array([])),
                                   AssertionError)
        assert not hv.raises_exception(lambda: hv.assert_not_none_nan(np.array([1])))
        assert not hv.raises_exception(lambda: hv.assert_not_none_nan(np.array([''])))

        # test pandas series
        assert hv.raises_exception(lambda: hv.assert_not_none_nan(pd.Series([1, np.nan, None])),
                                   AssertionError)
        assert hv.raises_exception(lambda: hv.assert_not_none_nan(pd.Series([1, np.nan])),
                                   AssertionError)
        assert hv.raises_exception(lambda: hv.assert_not_none_nan(pd.Series([1, None])),
                                   AssertionError)
        assert hv.raises_exception(lambda: hv.assert_not_none_nan(pd.Series([np.nan])),
                                   AssertionError)
        assert hv.raises_exception(lambda: hv.assert_not_none_nan(pd.Series([None])),
                                   AssertionError)
        assert hv.raises_exception(lambda: hv.assert_not_none_nan(pd.Series([], dtype=float)),
                                   AssertionError)
        assert not hv.raises_exception(lambda: hv.assert_not_none_nan(pd.Series([1])))
        assert not hv.raises_exception(lambda: hv.assert_not_none_nan(pd.Series([''])))

        # test pandas data.frame
        assert hv.raises_exception(lambda: hv.assert_not_none_nan(pd.DataFrame([[1, np.nan, None], [1, 2, 3]])),  # noqa
                                   AssertionError)
        assert hv.raises_exception(lambda: hv.assert_not_none_nan(pd.DataFrame([[1, np.nan], [1, 2]])),
                                   AssertionError)
        assert hv.raises_exception(lambda: hv.assert_not_none_nan(pd.DataFrame([[1, None], [1, 2]])),
                                   AssertionError)
        assert hv.raises_exception(lambda: hv.assert_not_none_nan(pd.DataFrame([[np.nan], [1]])),
                                   AssertionError)
        assert hv.raises_exception(lambda: hv.assert_not_none_nan(pd.DataFrame([[None], [1]])),
                                   AssertionError)
        assert hv.raises_exception(lambda: hv.assert_not_none_nan(pd.DataFrame([], dtype=float)),
                                   AssertionError)
        assert not hv.raises_exception(lambda: hv.assert_not_none_nan(pd.DataFrame([1])))
        assert not hv.raises_exception(lambda: hv.assert_not_none_nan(pd.DataFrame([[1], [1]])))
        assert not hv.raises_exception(lambda: hv.assert_not_none_nan(pd.DataFrame([[''], [1]])))

    def test_any_missing(self):
        assert hv.any_missing(None)  # noqa
        assert hv.any_missing(np.NaN)
        assert hv.any_missing('')  # noqa

        # test list
        assert hv.any_missing([1, np.nan, None])
        assert hv.any_missing([1, np.nan])
        assert hv.any_missing([1, None])
        assert hv.any_missing([np.nan])
        assert hv.any_missing([None])
        assert hv.any_missing([])
        assert hv.any_missing([''])
        assert hv.any_missing(['abc', ''])
        assert hv.any_missing([1, ''])
        assert not hv.any_missing([1])
        assert not hv.any_missing(['a'])

        # test pandas series
        assert hv.any_missing(pd.Series([1, np.nan, None]))
        assert hv.any_missing(pd.Series([1, np.nan]))
        assert hv.any_missing(pd.Series([1, None]))
        assert hv.any_missing(pd.Series([np.nan]))
        assert hv.any_missing(pd.Series([None]))
        assert hv.any_missing(pd.Series([], dtype=float))
        assert hv.any_missing(pd.Series(['']))
        assert hv.any_missing(pd.Series(['abc', '']))
        assert hv.any_missing(pd.Series([1, '']))
        assert not hv.any_missing(pd.Series([1]))
        assert not hv.any_missing(pd.Series(['a']))

        # test pandas data.frame
        assert hv.any_missing(pd.DataFrame([[1, np.nan, None], [1, 2, 3]]))
        assert hv.any_missing(pd.DataFrame([[1, np.nan], [1, 2]]))
        assert hv.any_missing(pd.DataFrame([[1, None], [1, 2]]))
        assert hv.any_missing(pd.DataFrame([[np.nan], [1]]))
        assert hv.any_missing(pd.DataFrame([[None], [1]]))
        assert hv.any_missing(pd.DataFrame([], dtype=float))
        assert hv.any_missing(pd.DataFrame([['abc', ''], ['abc', 'abc']]))
        assert hv.any_missing(pd.DataFrame(['']))
        assert not hv.any_missing(pd.DataFrame([1]))
        assert not hv.any_missing(pd.DataFrame([[1], [1]]))

    def test_assert_not_any_missing(self):
        assert hv.raises_exception(lambda: hv.assert_not_any_missing(None),  # noqa
                                   AssertionError)
        assert hv.raises_exception(lambda: hv.assert_not_any_missing(np.NaN),
                                   AssertionError)
        assert hv.raises_exception(lambda: hv.assert_not_any_missing(''),  # noqa
                                   AssertionError)

        # test list
        assert hv.raises_exception(lambda: hv.assert_not_any_missing([1, np.nan, None]),
                                   AssertionError)
        assert hv.raises_exception(lambda: hv.assert_not_any_missing([1, np.nan]),
                                   AssertionError)
        assert hv.raises_exception(lambda: hv.assert_not_any_missing([1, None]),
                                   AssertionError)
        assert hv.raises_exception(lambda: hv.assert_not_any_missing([np.nan]),
                                   AssertionError)
        assert hv.raises_exception(lambda: hv.assert_not_any_missing([None]),
                                   AssertionError)
        assert hv.raises_exception(lambda: hv.assert_not_any_missing([]),
                                   AssertionError)
        assert hv.raises_exception(lambda: hv.assert_not_any_missing(['']),
                                   AssertionError)
        assert hv.raises_exception(lambda: hv.assert_not_any_missing(['abc', '']),
                                   AssertionError)
        assert hv.raises_exception(lambda: hv.assert_not_any_missing([1, '']),
                                   AssertionError)
        assert not hv.raises_exception(lambda: hv.assert_not_any_missing([1]))
        assert not hv.raises_exception(lambda: hv.assert_not_any_missing(['a']))

        # test pandas series
        assert hv.raises_exception(lambda: hv.assert_not_any_missing(pd.Series([1, np.nan, None])),
                                   AssertionError)
        assert hv.raises_exception(lambda: hv.assert_not_any_missing(pd.Series([1, np.nan])),
                                   AssertionError)
        assert hv.raises_exception(lambda: hv.assert_not_any_missing(pd.Series([1, None])),
                                   AssertionError)
        assert hv.raises_exception(lambda: hv.assert_not_any_missing(pd.Series([np.nan])),
                                   AssertionError)
        assert hv.raises_exception(lambda: hv.assert_not_any_missing(pd.Series([None])),
                                   AssertionError)
        assert hv.raises_exception(lambda: hv.assert_not_any_missing(pd.Series([], dtype=float)),
                                   AssertionError)
        assert hv.raises_exception(lambda: hv.assert_not_any_missing(pd.Series([''])),
                                   AssertionError)
        assert hv.raises_exception(lambda: hv.assert_not_any_missing(pd.Series(['abc', ''])),
                                   AssertionError)
        assert hv.raises_exception(lambda: hv.assert_not_any_missing(pd.Series([1, ''])),
                                   AssertionError)
        assert not hv.raises_exception(lambda: hv.assert_not_any_missing(pd.Series([1])))
        assert not hv.raises_exception(lambda: hv.assert_not_any_missing(pd.Series(['a'])))

        # test pandas data.frame
        assert hv.raises_exception(lambda: hv.assert_not_any_missing(pd.DataFrame([[1, np.nan, None], [1, 2, 3]])),
                                   AssertionError)
        assert hv.raises_exception(lambda: hv.assert_not_any_missing(pd.DataFrame([[1, np.nan], [1, 2]])),
                                   AssertionError)
        assert hv.raises_exception(lambda: hv.assert_not_any_missing(pd.DataFrame([[1, None], [1, 2]])),
                                   AssertionError)
        assert hv.raises_exception(lambda: hv.assert_not_any_missing(pd.DataFrame([[np.nan], [1]])),
                                   AssertionError)
        assert hv.raises_exception(lambda: hv.assert_not_any_missing(pd.DataFrame([[None], [1]])),
                                   AssertionError)
        assert hv.raises_exception(lambda: hv.assert_not_any_missing(pd.DataFrame([], dtype=float)),
                                   AssertionError)
        assert hv.raises_exception(lambda: hv.assert_not_any_missing(pd.DataFrame([['abc', ''], ['abc', 'abc']])),
                                   AssertionError)
        assert hv.raises_exception(lambda: hv.assert_not_any_missing(pd.DataFrame([''])),
                                   AssertionError)
        assert not hv.raises_exception(lambda: hv.assert_not_any_missing(pd.DataFrame([1])))
        assert not hv.raises_exception(lambda: hv.assert_not_any_missing(pd.DataFrame([[1], [1]])))

    def test_any_duplicated(self):
        # test list
        assert not hv.any_duplicated([''])
        assert not hv.any_duplicated(['', 1])
        assert not hv.any_duplicated(['', 1, None])

        assert hv.any_duplicated(['', 1, ''])
        assert hv.any_duplicated(['', 1, 1])
        assert hv.any_duplicated(['', 1, None, None])

        # test pd.Series
        assert not hv.any_duplicated(pd.Series(['']))
        assert not hv.any_duplicated(pd.Series(['', 1]))
        assert not hv.any_duplicated(pd.Series(['', 1, None]))

        assert hv.any_duplicated(pd.Series(['', 1, '']))
        assert hv.any_duplicated(pd.Series(['', 1, 1]))
        assert hv.any_duplicated(pd.Series(['', 1, None, None]))

    def test_assert_not_duplicated(self):
        # test list
        assert not hv.raises_exception(lambda: hv.assert_not_duplicated(['']))
        assert not hv.raises_exception(lambda: hv.assert_not_duplicated(['', 1]))
        assert not hv.raises_exception(lambda: hv.assert_not_duplicated(['', 1, None]))

        assert hv.raises_exception(lambda: hv.assert_not_duplicated(['', 1, '']),
                                   AssertionError)
        assert hv.raises_exception(lambda: hv.assert_not_duplicated(['', 1, 1]),
                                   AssertionError)
        assert hv.raises_exception(lambda: hv.assert_not_duplicated(['', 1, None, None]),
                                   AssertionError)

        # test pd.Series
        assert not hv.raises_exception(lambda: hv.assert_not_duplicated(pd.Series([''])))
        assert not hv.raises_exception(lambda: hv.assert_not_duplicated(pd.Series(['', 1])))
        assert not hv.raises_exception(lambda: hv.assert_not_duplicated(pd.Series(['', 1, None])))

        assert hv.raises_exception(lambda: hv.assert_not_duplicated(pd.Series(['', 1, ''])),
                                   AssertionError)
        assert hv.raises_exception(lambda: hv.assert_not_duplicated(pd.Series(['', 1, 1])),
                                   AssertionError)
        assert hv.raises_exception(lambda: hv.assert_not_duplicated(pd.Series(['', 1, None, None])),
                                   AssertionError)

    def test_raises_exception(self):

        def my_function_exception():
            raise ValueError()

        def my_function_runs():
            return True

        assert hv.raises_exception(my_function_exception)
        # should return True since my_function_exception raises ValueError
        assert hv.raises_exception(my_function_exception, ValueError)
        # should return False since my_function_exception raises ValueError, not TypeError
        assert not hv.raises_exception(my_function_exception, TypeError)
        assert not hv.raises_exception(my_function_runs)

    def test_assert_true(self):
        hv.assert_true(True)
        assert isinstance(np.bool_(True), np.bool_)
        hv.assert_true(np.bool_(True))

        assert hv.raises_exception(lambda: hv.assert_true([]), TypeError)  # noqa
        assert hv.raises_exception(lambda: hv.assert_true([True]), TypeError)  # noqa

        raised_exception = False
        try:
            hv.assert_true(False)
        except AssertionError:
            raised_exception = True
        assert raised_exception

        raised_exception = False
        try:
            hv.assert_true(False, message='my message')
        except AssertionError as error:
            raised_exception = True
            assert error.args[0] == 'my message'
        assert raised_exception

    def test_assert_false(self):
        hv.assert_false(False)
        assert isinstance(np.bool_(False), np.bool_)
        hv.assert_false(np.bool_(False))

        assert hv.raises_exception(lambda: hv.assert_false([]), TypeError)  # noqa
        assert hv.raises_exception(lambda: hv.assert_false([False]), TypeError)  # noqa

        raised_exception = False
        try:
            hv.assert_false(True)
        except AssertionError:
            raised_exception = True
        assert raised_exception

        raised_exception = False
        try:
            hv.assert_false(True, message='my message')
        except AssertionError as error:
            raised_exception = True
            assert error.args[0] == 'my message'
        assert raised_exception

    def test_assert_all(self):
        cases = [
            [True],
            [True, True],
            np.array([True]),
            np.array([True, True]),
            pd.Series([True]),
            pd.Series([True, True]),
            pd.DataFrame([True]),
            pd.DataFrame([True, True]),
            pd.DataFrame([[True, True], [True, True]]),
        ]
        passing_cases = [not hv.raises_exception(lambda: hv.assert_all(case),
                                                 AssertionError)
                         for case in cases]
        assert all(passing_cases)

        cases = [
            [False],
            [True, False],
            np.array([False]),
            np.array([True, False]),
            pd.Series([False]),
            pd.Series([True, False]),
            pd.DataFrame([False]),
            pd.DataFrame([True, False]),
            pd.DataFrame([[True, True], [True, False]]),
        ]
        passing_cases = [hv.raises_exception(lambda: hv.assert_all(case),
                                             AssertionError)
                         for case in cases]
        assert all(passing_cases)

    def test_assert_not_any(self):
        cases = [
            [False],
            [False, False],
            np.array([False]),
            np.array([False, False]),
            pd.Series([False]),
            pd.Series([False, False]),
            pd.DataFrame([False]),
            pd.DataFrame([False, False]),
            pd.DataFrame([[False, False], [False, False]]),
        ]
        passing_cases = [not hv.raises_exception(lambda: hv.assert_not_any(case),
                                                 AssertionError)
                         for case in cases]
        assert all(passing_cases)

        cases = [
            [True],
            [True, False],
            np.array([True]),
            np.array([True, False]),
            pd.Series([True]),
            pd.Series([True, False]),
            pd.DataFrame([True]),
            pd.DataFrame([True, False]),
            pd.DataFrame([[False, False], [False, True]]),
        ]
        passing_cases = [hv.raises_exception(lambda: hv.assert_not_any(case),
                                             AssertionError)
                         for case in cases]
        assert all(passing_cases)

    def test_dataframes_match(self):

        dataframe_1 = pd.DataFrame({'col_floats': [1.123456789, 2.123456789, 3.123456789],
                                    'col_strings': ['a', 'b', 'c'],
                                    'col_enums': [hs.RoundTo.NONE, hs.RoundTo.AUTO, hs.RoundTo.THOUSANDS],
                                    'col_dates': pd.date_range('2021-01-01', periods=3)})

        # test assertion errors when passing in invalid data
        assert hv.raises_exception(lambda: hv.dataframes_match(dataframes=dataframe_1),  # noqa
                                   exception_type=AssertionError)
        assert hv.raises_exception(lambda: hv.dataframes_match(dataframes=[dataframe_1]),
                                   exception_type=AssertionError)

        # test that there are no side effects; e.g. we set the index/column values if we ignore them
        dataframe_1_original = dataframe_1.copy()
        dataframe_2 = dataframe_1.copy()
        dataframe_2.index = ['a', 'b', 'c']
        dataframe_2.columns = ['a', 'b', 'c', 'd']
        dataframe_2_original = dataframe_2.copy()
        assert hv.dataframes_match(dataframes=[dataframe_1, dataframe_2],
                                   float_tolerance=1,
                                   ignore_indexes=True,
                                   ignore_column_names=True)
        assert dataframe_1.equals(dataframe_1_original)
        assert (dataframe_1.index == dataframe_1_original.index).all()
        assert (dataframe_1.columns == dataframe_1_original.columns).all()
        assert dataframe_2.equals(dataframe_2_original)
        assert (dataframe_2.index == dataframe_2_original.index).all()
        assert (dataframe_2.columns == dataframe_2_original.columns).all()

        assert hv.dataframes_match(dataframes=[dataframe_1, dataframe_1])
        assert hv.dataframes_match(dataframes=[dataframe_1, dataframe_1, dataframe_1])
        assert hv.dataframes_match(dataframes=[dataframe_1, dataframe_1.copy(), dataframe_1.copy()])

        assert hv.dataframes_match(dataframes=[dataframe_1, dataframe_1.round(6)])
        assert not hv.dataframes_match(dataframes=[dataframe_1, dataframe_1.round(5)])
        assert not hv.dataframes_match(dataframes=[dataframe_1, dataframe_1, dataframe_1.round(5)])
        assert hv.dataframes_match(dataframes=[dataframe_1, dataframe_1.round(5)], float_tolerance=5)
        assert hv.dataframes_match(dataframes=[dataframe_1, dataframe_1.round(6), dataframe_1.round(5)],
                                   float_tolerance=5)

        dataframe_2 = dataframe_1.copy()
        dataframe_2.iat[0, 0] = dataframe_2.iat[0, 0] - 0.000001
        assert not hv.dataframes_match(dataframes=[dataframe_1, dataframe_2])
        assert not hv.dataframes_match(dataframes=[dataframe_1, dataframe_1.copy(), dataframe_2])

        dataframe_2 = dataframe_1.copy()
        dataframe_2.iat[1, 1] = 'c'
        assert not hv.dataframes_match(dataframes=[dataframe_1, dataframe_2])
        assert not hv.dataframes_match(dataframes=[dataframe_1, dataframe_1.copy(), dataframe_2])

        dataframe_2 = dataframe_1.copy()
        dataframe_2.iat[2, 2] = hs.RoundTo.MILLIONS
        assert not hv.dataframes_match(dataframes=[dataframe_1, dataframe_2])
        assert not hv.dataframes_match(dataframes=[dataframe_1, dataframe_1.copy(), dataframe_2])

        dataframe_2 = dataframe_1.copy()
        dataframe_2.iat[2, 3] = dataframe_2.iat[2, 3] + timedelta(seconds=1)
        assert not hv.dataframes_match(dataframes=[dataframe_1, dataframe_2])
        assert not hv.dataframes_match(dataframes=[dataframe_1, dataframe_1.copy(), dataframe_2])

        dataframe_2 = dataframe_1.copy()
        dataframe_2.iat[2, 3] = dataframe_2.iat[2, 3] + timedelta(seconds=1) - timedelta(seconds=1)
        assert hv.dataframes_match(dataframes=[dataframe_1, dataframe_2])
        assert hv.dataframes_match(dataframes=[dataframe_1, dataframe_1.copy(), dataframe_2])

        dataframe_2 = dataframe_1.copy()
        dataframe_2.iat[0, 0] = np.NaN
        assert not hv.dataframes_match(dataframes=[dataframe_1, dataframe_2])
        assert not hv.dataframes_match(dataframes=[dataframe_1, dataframe_1.copy(), dataframe_2])

        dataframe_2 = dataframe_1.copy()
        dataframe_2.iat[1, 1] = np.NaN
        assert not hv.dataframes_match(dataframes=[dataframe_1, dataframe_2])
        assert not hv.dataframes_match(dataframes=[dataframe_1, dataframe_1.copy(), dataframe_2])

        dataframe_2 = dataframe_1.copy()
        dataframe_2.iat[1, 2] = np.NaN
        assert not hv.dataframes_match(dataframes=[dataframe_1, dataframe_2])
        assert not hv.dataframes_match(dataframes=[dataframe_1, dataframe_1.copy(), dataframe_2])

        dataframe_2 = dataframe_1.copy()
        dataframe_2.iat[1, 3] = np.NaN
        assert not hv.dataframes_match(dataframes=[dataframe_1, dataframe_2])
        assert not hv.dataframes_match(dataframes=[dataframe_1, dataframe_1.copy(), dataframe_2])

        dataframe_2 = dataframe_1.copy()
        dataframe_2.columns = ['a', 'b', 'c', 'd']
        dataframe_2.index = ['a', 'b', 'c']
        assert hv.dataframes_match(dataframes=[dataframe_1, dataframe_2])
        assert hv.dataframes_match(dataframes=[dataframe_1, dataframe_2, dataframe_2])
        assert not hv.dataframes_match(dataframes=[dataframe_1, dataframe_2], ignore_indexes=False)
        assert not hv.dataframes_match(dataframes=[dataframe_1, dataframe_2], ignore_column_names=False)
        assert not hv.dataframes_match(dataframes=[dataframe_1, dataframe_2],
                                       ignore_indexes=False,
                                       ignore_column_names=False)

    def test_assert_dataframes_match(self):
        dataframe_1 = pd.DataFrame({'col': [1.123456789, 2.123456789, 3.123456789]})

        # test assertion errors when passing in invalid data
        assert hv.raises_exception(lambda: hv.assert_dataframes_match(dataframes=dataframe_1),  # noqa
                                   exception_type=AssertionError)
        assert hv.raises_exception(lambda: hv.assert_dataframes_match(dataframes=[dataframe_1]),
                                   exception_type=AssertionError)

        assert hv.assert_dataframes_match(dataframes=[dataframe_1, dataframe_1]) is None

        dataframe_2 = dataframe_1.copy()
        dataframe_2.iat[0, 0] = np.nan
        assert hv.raises_exception(lambda: hv.assert_dataframes_match(dataframes=[dataframe_1, dataframe_2]),
                                   exception_type=AssertionError)

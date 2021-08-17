"""
A collection of functions that assist in validation/comparison of data and conditions.
"""
from typing import List, Union, Callable, Type
import numpy as np
import pandas as pd


def any_none_nan(values: Union[List, np.ndarray, pd.Series, pd.DataFrame]) -> bool:
    """
    Returns `True` if any item in `values` are `None`, `np.Nan`, or if the length of `values` is `0`.
    For numeric types only.

    Parameters
    ----------
    values : list, np.ndarray, pd.Series, pd.DataFrame
        A collection of values to check.

    Returns
    -------
    bool - True if any item in `values` are None/np.NaN
    """
    # pylint: disable=too-many-return-statements
    if values is None or values is np.NaN or len(values) == 0:  # pylint: disable=nan-comparison
        return True

    if isinstance(values, pd.Series):
        return values.isnull().any() or values.isna().any()  # noqa

    if isinstance(values, pd.DataFrame):
        return values.isnull().any().any() or values.isna().any().any()  # noqa

    if None in values:
        return True

    try:
        if np.isnan(values).any():
            return True
    except TypeError:
        return False

    return False


def assert_not_none_nan(values: Union[List, np.ndarray, pd.Series, pd.DataFrame]) -> None:
    """
    Raises an AssertionError if any item in `values` are `None`, `np.Nan`, or if the length of `values` is
    `0`.
    For numeric types only.

    Parameters
    ----------
    values : list, np.ndarray, pd.Series, pd.DataFrame
        A collection of values to check.

    Returns
    -------
    None
    """
    assert_false(any_none_nan(values), message='None/NaN Values Found')


def any_missing(values: Union[List, pd.Series, pd.DataFrame]) -> bool:
    """
    Returns `True` if any item in `values` are `None`, `np.Nan`, an empty string (i.e. '') or if the length of
    `values` is `0`.

    Parameters
    ----------
    values : list, pd.Series, pd.DataFrame
        A collection of values to check.

    Returns
    -------
    bool - True if any item in `values` are None/np.NaN/''
    """
    if any_none_nan(values):
        return True

    if isinstance(values, pd.Series):
        return values.isin(['']).any()  # noqa

    if isinstance(values, pd.DataFrame):
        return values.isin(['']).any().any()  # noqa

    if '' in values:
        return True

    return False


def assert_not_any_missing(values: Union[List, pd.Series, pd.DataFrame]) -> None:
    """
    Raises an AssertionError if any item in `values` are `None`, `np.Nan`, an empty string (i.e. '') or if the
    length of `values` is `0`.

    Parameters
    ----------
    values : list, pd.Series, pd.DataFrame
        A collection of values to check.

    Returns
    -------
    bool - True if any item in `values` are None/np.NaN/''
    """
    assert_false(any_missing(values), message='Missing Values Found')


def any_duplicated(values: Union[List, np.ndarray, pd.Series]) -> bool:
    """
    Returns `True` if any items in `values` are duplicated.

    Parameters
    ----------
    values : list, np.ndarray, pd.Series
        A collection of values to check.

    Returns
    -------
    bool
    """
    return len(values) != len(set(values))


def assert_not_duplicated(values: Union[List, np.ndarray, pd.Series]) -> None:
    """
    Raises an AssertionError if any items in `values` are duplicated.

    Parameters
    ----------
    values : list, np.ndarray, pd.Series
        A collection of values to check.

    Returns
    -------
    """
    assert_false(any_duplicated(values), message='Duplicate Values Found')


def assert_all(values: Union[List, np.ndarray, pd.Series, pd.DataFrame]) -> None:
    """
    Raises an `AssertionError` unless all items in `values` are `True`

    Parameters
    ----------
    values : list, np.ndarray, pd.Series, pd.DataFrame
        A collection of values to check.

    Returns
    -------
    None
    """
    if isinstance(values, pd.Series):
        if not values.all():  # noqa
            raise AssertionError('Not All True')
    elif isinstance(values, pd.DataFrame):
        if not values.all().all():  # noqa
            raise AssertionError('Not All True')
    else:
        if not all(values):
            raise AssertionError('Not All True')


def assert_not_any(values: Union[List, np.ndarray, pd.Series, pd.DataFrame]) -> None:
    """
    Raises an `AssertionError` if any items in `values` are `True`

    Parameters
    ----------
    values : list, np.ndarray, pd.Series, pd.DataFrame
        A collection of values to check.

    Returns
    -------
    None
    """
    if isinstance(values, pd.Series):
        assert_false(values.any(), message='Found True')  # noqa

    elif isinstance(values, pd.DataFrame):
        assert_false(values.any().any(), message='Found True')  # noqa

    else:
        assert_false(any(values), message='Found True')


def assert_true(condition: bool, message: str = 'Condition Not True') -> None:
    """
    Raises an AssertionError if `condition` is not True
    """
    if not isinstance(condition, (bool, np.bool_)):
        raise TypeError('condition should be boolean')

    if not condition:
        raise AssertionError(message)


def assert_false(condition: bool, message: str = 'Condition True') -> None:
    """
    Raises an AssertionError if `condition` is not False
    """
    if not isinstance(condition, (bool, np.bool_)):
        raise TypeError('condition should be boolean')

    if condition:
        raise AssertionError(message)


def raises_exception(function: Callable, exception_type: Type = None) -> bool:
    """
    Returns True if `function` raises an Exception; returns False if `function` runs without raising an
    Exception.

    Keyword arguments:
    function -- a function
    """
    try:
        function()
        return False
    except Exception as exception:  # pylint: disable=broad-except
        if exception_type:
            return isinstance(exception, exception_type)

        return True


def dataframes_match(dataframes: List[pd.DataFrame],
                     float_tolerance: int = 6,
                     ignore_indexes: bool = True,
                     ignore_column_names: bool = True) -> bool:
    """
    Because floating point numbers are difficult to accurate represent, when comparing multiple DataFrames,
    this function first rounds any numeric columns to the number of decimal points indicated
    `float_tolerance`.

    Parameters
    ----------
    dataframes : list of pd.DataFrame
        Two or more dataframes to compare against each other and test for equality

    float_tolerance: int
        numeric columns will be rounded to the number of digits to the right of the decimal specified by
        this parameter.

    ignore_indexes: bool
        if True, the indexes of each DataFrame will be ignored for considering equality

    ignore_column_names: bool
        if True, the column names of each DataFrame will be ignored for considering equality
    """
    assert isinstance(dataframes, list)
    assert len(dataframes) >= 2

    first_dataframe = dataframes[0].round(float_tolerance)

    def first_dataframe_equals_other(other_dataframe):
        if first_dataframe.shape != other_dataframe.shape:
            return False

        if ignore_indexes or ignore_column_names:
            # if either of these are True, then we are going to change the index and/or columns, but
            # python is pass-by-reference so we don't want to change the original DataFrame object.
            other_dataframe = other_dataframe.copy()

        if ignore_indexes:
            other_dataframe.index = first_dataframe.index

        if ignore_column_names:
            other_dataframe.columns = first_dataframe.columns

        return first_dataframe.equals(other_dataframe.round(float_tolerance))

    # compare the first dataframe to the rest of the dataframes, after rounding each to the tolerance, and
    # performing other modifications
    # check if all results are True
    return all(first_dataframe_equals_other(x) for x in dataframes[1:])


def assert_dataframes_match(dataframes: List[pd.DataFrame],
                            float_tolerance: int = 6,
                            ignore_indexes: bool = True,
                            ignore_column_names: bool = True,
                            message: str = 'Dataframes do not match') -> None:
    """
    Raises an assertion error

    Parameters
    ----------
    dataframes : list of pd.DataFrame
        Two or more dataframes to compare against each other and test for equality

    float_tolerance: int
        numeric columns will be rounded to the number of digits to the right of the decimal specified by
        this parameter.

    ignore_indexes: bool
        if True, the indexes of each DataFrame will be ignored for considering equality

    ignore_column_names: bool
        if True, the column names of each DataFrame will be ignored for considering equality

    message: str
        message to pass to AssertionError
    """
    if not dataframes_match(dataframes=dataframes,
                            float_tolerance=float_tolerance,
                            ignore_indexes=ignore_indexes,
                            ignore_column_names=ignore_column_names):
        raise AssertionError(message)

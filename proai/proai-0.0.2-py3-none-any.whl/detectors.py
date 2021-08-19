""" Detectors for the 10 different types of data science variables/data/features

1. numerical
2. categorical (red, green, blue)
3. tags (nonexclusive categories such as [fiction, science, science-fiction, fantasy, liked])
4. ordinal (small, medium, large)
5. date/time/datetime
6. location (lat/lon, address, zip code, etc)
7. natural language (a description or note with high cardinality for that dataset)
8. image
9. video
10. audio (or time series)
"""
import pandas as pd
import numpy as np

NULL_VALUES = set(['None', 'null', "'", '"', ""])
NULL_ZERO_VALUES = NULL_VALUES.union(set(['0'] + ['0.' + z for z in ('0' * i for i in range(10))]))

NULL_VALUES_LOWERED = set((str(x).lower().strip() for x in NULL_VALUES))


def is_null(obj):
    r""" Is the provided object processable as a float

    >>> is_null(np.nan)
    True
    >>> is_null('nan')
    True
    >>> is_null('nuLl')
    True
    >>> is_null(42)
    False
    >>> is_null(None)
    True
    >>> is_null(' None\n   ')
    True
    """
    try:
        obj = float(obj)
        return np.isnan(obj)
    except (ValueError, TypeError):
        pass
    obj = str(obj).strip().lower()
    if obj in NULL_VALUES_LOWERED:
        return True
    return False


def is_number(obj):
    r""" Is the provided object processable as a float

    >>> is_number('NaN')
    True
    >>> is_number('hello world')
    False
    >>> is_number(42)
    True
    """
    try:
        float(obj)
        return True
    except ValueError:
        return False


def is_numerical(series: (pd.Series, list), min_purity=1.0):
    r""" Return True if the pd.Series can be processed as a numerical feature for DS

    >>> is_numerical([1, 2, 3])
    True
    >>> is_numerical([1, 2, 3, 'nope'])
    False
    >>> is_numerical([1, 2, 3, 'nope'], min_purity=0.7)
    True
    >>> is_numerical([1, 2, 3, 'None'])
    False
    """
    # TODO: incorporate magic load_series function
    if not isinstance(series, pd.Series):
        series = pd.Series(series)
    mask = series.apply(is_number)
    min_purity = min_purity if isinstance(min_purity, float) else min_purity / len(mask)
    return mask.sum() / len(mask) >= min_purity

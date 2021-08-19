import numpy as np
import pandas as pd
import pytest

import trifacta as tp


@pytest.fixture(scope='session')
def df():
    return pd.DataFrame({'letters': ['a', 'b', 'c'], 'numbers': [1, 2, 3]})


@pytest.fixture(scope='session')
def typesDf():
    # Time zone
    dttzType = pd.DatetimeTZDtype(tz='UTC')
    # Categorical
    categoricalType = pd.CategoricalDtype(categories=['b', 'a'], ordered=True)
    # Time span
    periodType = pd.PeriodDtype(freq='D')
    # Sparse data
    sparseIntType = pd.SparseDtype(dtype=int, fill_value=0)
    # IntervalIndex
    interval64Type = pd.IntervalDtype(subtype='int64')
    # Nullable Integer
    nullintType = pd.Int64Dtype()
    # String
    stringType = pd.StringDtype()
    # Nullable Boolean
    nullboolType = pd.BooleanDtype()
    # based on discussion at https://stackoverflow.com/questions/29245848/what-are-all-the-dtypes-that-pandas-recognizes
    df = pd.DataFrame.from_dict({'float': [1.0, np.NaN],
                                 'int': [1, 2],
                                 'bool': [True, False],
                                 'interval': [pd.Interval(left=0, right=5), pd.Interval(left=0, right=0)],
                                 'datetimetz': ['2005-02-25T03:30', 'NaT'],
                                 'categorical': ['a', pd.NA],
                                 'period': ['23H', 'NaT'],
                                 'sparseInt': [1, 0],
                                 'int64': [100000000000000, pd.NA],
                                 'string': ['test', pd.NA],
                                 'boolean': [True, pd.NA]
                                 })
    df = df.astype(dtype={
        'float': float,
        'int': int,
        'bool': bool,
        'interval': interval64Type,
        'datetimetz': dttzType,
        'categorical': categoricalType,
        'period': periodType,
        'sparseInt': sparseIntType,
        'int64': nullintType,
        'string': stringType,
        'boolean': nullboolType
    })
    return (df)


@pytest.fixture(scope='session')
def csv(tmpdir_factory, df):
    fn = tmpdir_factory.mktemp("data").join('input.csv')
    df.to_csv(fn,index=False,header=False)
    return fn


@pytest.fixture(scope='session')
def wf(df):
    wf = tp.wrangle(df)
    return wf


@pytest.fixture(scope='session')
def wf2(csv):
    wf2 = tp.wrangle(csv)
    return wf2


@pytest.fixture(scope='session')
def wfmany(csv):
    df1 = pd.DataFrame({'letters': ['a', 'b', 'c'], 'numbers': [1, 2, 3]})
    df2 = pd.DataFrame({'letters': ['x', 'y', 'z'], 'numbers': [100, 200, 300]})
    dflist = [df1, df2]
    wfmany = tp.wrangle(dflist)
    df3 = pd.DataFrame({'dogs': ['fido', 'spot', 'snoopy'], 'bones': ['shank', 'T', 'ankle'],
                        'snacks': ['snausage', 'kibble', 'rubber chicken']})
    wfmany.add_datasets(df3)
    return wfmany

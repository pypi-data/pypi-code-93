import pandas as pd

from profiling.importance import varimp


def predict_second_column(df):
    """Returns first column"""
    return df.iloc[:, 1].astype("float")


df = pd.DataFrame.from_dict(
    {
        "Object": [None, "", "c"],
        "Integer": [1, 2, 3],
        "Float": [1.0, 2.0, 3.0],
        "Categorical": pd.Series(["a", "b", "c"], dtype="category"),
        "Index": ["a", "b", "c"],
    }
).set_index("Index")


def test_order():
    chart, varlist = varimp(predict_second_column, df)
    second_col = df.columns[1]
    assert varlist[0] == second_col
    assert chart.data["Variable"].iloc[0] == second_col
    assert chart.data["Importance"].iloc[0] > 0
    assert all(chart.data["Importance"].iloc[1:] == 0.0)


def test_subset():
    columns = df.columns.to_list()
    profile_columns = columns[1:]
    _, varlist = varimp(predict_second_column, df, profile_columns=profile_columns)
    assert columns[0] not in varlist
    assert columns[1] in varlist


def test_metric():
    chart, _ = varimp(predict_second_column, df, metric="Mae")
    assert chart.data["Variable"].iloc[0] == df.columns[1]

import pandas as pd

def make_dummies(series):
    df = pd.get_dummies(series,drop_first=True)
    df.columns = list(map(lambda x: '{}_'.format(series.name) + str(x),list(df.columns)))
    return df
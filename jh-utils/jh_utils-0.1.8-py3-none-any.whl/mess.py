import pandas as pd

##
def na_by_column(df):
    ret = df.isnull().mean()
    return ret
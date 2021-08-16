from pandas import DataFrame as PandasDF
from pyspark.sql import DataFrame as SparkDF
from ...collections import get_duplicates

def assert_columns_are_unique(df):
    """
    :type df: PandasDF or SparkDF
    """
    df_columns = list(df.columns)
    duplicates = get_duplicates(df_columns)

    if len(duplicates) > 0:
        message = f'Duplicate columns: "{", ".join(duplicates)}"'
        print(message)
        raise KeyError(message)
    else:
        return True

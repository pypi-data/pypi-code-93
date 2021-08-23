
import io
import os
import pandas as pd
from pyspark.sql import SparkSession
from pandas.core.frame import DataFrame as Pandas_DataFrame
from pyspark.sql.dataframe import DataFrame as PySpark_DataFrame

"""
"   Converts pyspark or pandas dataframe to CSV string
"""
def df_to_csv(df, df_type):
    """
    @param::df: 'pyspark.sql.dataframe.DataFrame' or 'pandas.core.frame.DataFrame' object
    @param::df_type: dataframe type represented as a string
    Returns CSV data represented as a string
    """
    _PANDAS = 'pandas'
    _PYSPARK = 'pyspark'
    supported_df = (Pandas_DataFrame, PySpark_DataFrame)
    supported_type = {_PANDAS, _PYSPARK}

    try:
        if not isinstance(df, supported_df):
            raise TypeError(f'> df_to_csv: df must be an instance of one of {str(supported_df)}.')
        if df_type not in supported_type:
            raise IndexError(f'> df_to_csv: df_type "{df_type}" is invalid for dataframe-to-csv conversion.')

        to_csv_functions = {
            _PANDAS: lambda df: df.to_csv(index=False),
            _PYSPARK: lambda df: df.toPandas().to_csv(index=False)
        }
        to_csv = to_csv_functions.get(df_type)
        return to_csv(df)
    except Exception as e:
        print(e)
        raise

"""
"   Converts CSV to the appropriate dataframe type
"""
def csv_to_df(csv, df_type):
    """
    @param::csv: CSV data represented as a string or path to csv file
    @param::df_type: dataframe type represented as a string
    Returns 'pyspark.sql.dataframe.DataFrame' or 'pandas.core.frame.DataFrame' object
    """
    _PANDAS = 'pandas'
    _PYSPARK = 'pyspark'
    supported_type = {_PANDAS, _PYSPARK}

    try:
        if df_type not in supported_type:
            raise IndexError(f'> csv_to_df: df_type "{df_type}" is invalid for csv-to-dataframe conversion.')

        to_df_functions = {
            _PANDAS: csv_to_pandas_df,
            _PYSPARK: csv_to_pyspark_df
        }
        to_df = to_df_functions.get(df_type)
        return to_df(csv)
    except Exception as e:
        print(e)
        raise

"""
"   Converts CSV to 'pandas.core.frame.DataFrame' object
"""
def csv_to_pandas_df(csv):
    """
    @param::csv: CSV data represented as a string or path to csv file
    """
    if not isinstance(csv, str):
        raise TypeError('> csv_to_pandas_df: not a valid csv string or file')

    if os.path.isfile(csv):
        return pd.read_csv(csv)
    else:
        text_stream_csv = io.StringIO(csv)
        return pd.read_csv(text_stream_csv)

"""
"   Converts CSV to 'pyspark.sql.dataframe.DataFrame' object
"""
def csv_to_pyspark_df(csv):
    """
    @param::csv: CSV data represented as a string or path to csv file
    """
    if not isinstance(csv, str):
        raise TypeError('> csv_to_pyspark_df: not a valid csv string or file')

    spark = (SparkSession.builder
             .appName("dimsum")
             .getOrCreate())

    if os.path.isfile(csv):
        return spark.read.csv(csv, header=True)
    else:
        sc = spark.sparkContext
        csv_rdd = sc.parallelize(csv.split('\n'))
        return spark.read.csv(csv_rdd, header=True)

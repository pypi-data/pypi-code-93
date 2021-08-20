from pandas import DataFrame  # type: ignore


def average_weekly_data(tab_data_set) -> DataFrame:
    """
    This function takes into Azure dataset of the average weekly data  and 
    returns a pandas dataframe

    tab_data_set: Azure tabular dataset
    """
    data: DataFrame = tab_data_set.to_pandas_dataframe()
    data['houroftheweek_average'] = data['houroftheweek_average'].astype('float32')

    return data

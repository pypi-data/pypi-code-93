from pandas import DataFrame


def hourofday(df: DataFrame) -> DataFrame:
    """
    This function adds day of week as a feature to the dataframe  and 
    returns just the new feature and substation_id as dataframe

    # Parameters
    --------------
    df: Dataframe with datetime index
    substation_id: refers to column name that keeps substation IDs

    # Returns
    --------------
    Pandas dataframe
    
    """
    # # Create hours of day as a new feature (for example: 0-23)
    # initial_index: DatetimeIndex = df.index if isinstance(
    #     df.index, DatetimeIndex) else pd.to_datetime(df.index)
    # df["hourofday"] = initial_index.hour.astype(np.float32)
    # return df

    # Create hours of day as a new feature (for example: 0-23)
    df['hourofday'] = df.index.hour
    df['hourofday'] = df['hourofday'].astype('float32')
    return df

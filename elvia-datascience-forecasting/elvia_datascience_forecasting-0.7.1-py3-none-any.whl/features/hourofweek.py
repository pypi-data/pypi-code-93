from pandas import DataFrame


def hourofweek(df: DataFrame) -> DataFrame:
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
    # Create day of week as a new feature (for example: 0-monday, 6-sunday)
    df["hourofweek"] = df["dayofweek"] * 24 + df['hourofday']
    df['hourofweek'] = df['hourofweek'].astype('float32')

    return df

from numpy import sin, cos, pi 
from pandas import DataFrame


def sin_cos_transformation(df: DataFrame, col: str,
                           max_val: int) -> DataFrame:
    """
    This function takes in dataframe with cyclical features and apply sine and cosine transformations to the features

    # Parameters
    --------------
    df      : Pandas dataframe
    col     : The column name that will be transformed
    max_val : Maximum value in the col feature 

    # Returns
    --------------
    A pandas dataframe with the transformed features
    """
    df[col + '_sin'] = sin(2 * pi * df[col] /
                              max_val)  # sine transformation
    df[col + '_sin'] = df[col + '_sin'].astype('float32')

    df[col + '_cos'] = cos(2 * pi * df[col] /
                              max_val)  # cosine transformation
    df[col + '_cos'] = df[col + '_cos'].astype('float32')

    return df

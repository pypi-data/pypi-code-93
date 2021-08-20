import json
from pandas import DataFrame, to_datetime, date_range
from datetime import datetime


def national_holiday(df: DataFrame, path_holiday: str = '') -> DataFrame:
    '''
    Loads Norwegian national holidays and adds true if the index is a holiday to the dateframe.
    Note that Sunday is considered a holiday in this set. 

    # Parameters
    --------------
    df          : Dataframe
    path_holiday: The path of the json file that contains dates of national holidays

    # Returns
    --------------
    A dataframe of natioanal holidays that consist of True/False

    '''

    df_holiday = df.copy()
    # Read the json file with holidays
    with open(path_holiday, 'r') as fn:
        h_n = json.load(fn)

    #  holidays_dt contains datetime index of the national holidays i.e Palmesøndag, Grunnlovsdag etc.
    holidays_dt = to_datetime([])
    # The loop takes dates of the national holidays and append them to holidays_dt as datetime
    for country_ferie in h_n['data']['national_holiday']:
        # Return a fixed frequency DatetimeIndex.
        vec = date_range(start=datetime.strptime(
            country_ferie['date_start'], '%Y-%m-%d'),
                            end=datetime.strptime(country_ferie['date_stop'],
                                                  '%Y-%m-%d'),
                            freq='D',
                            tz='Europe/Oslo',
                            closed='left')
        if holidays_dt.empty:
            holidays_dt = vec
        else:
            holidays_dt = holidays_dt.append(vec)

    # Create a holiday dataframe from the datetimes
    country_level_holiday = holidays_dt.to_frame().copy()
    # Creates a column with dates in the main dataframe
    frame = DataFrame()
    frame['date'] = df_holiday.index.unique().date
    # Check if datetime is holiday and add True/False.
    frame['national_holiday'] = frame['date'].isin(
        country_level_holiday.index.date).values
    # set unique index of df_holiday as frame index
    frame.index = df_holiday.index.unique()
    frame.drop('date', axis=1, inplace=True)

    return frame

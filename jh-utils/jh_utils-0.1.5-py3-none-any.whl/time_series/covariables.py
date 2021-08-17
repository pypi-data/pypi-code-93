import pandas as pd
import numpy as np

def hours_by_day(freq):
    freq = freq.upper()
    if freq == '1H':
        return 24
    if freq == '2H':
        return 12
    if freq == '3H':
        return 8
    if freq == '4H':
        return 6
    if freq == '6H':
        return 4
    if freq == '8H':
        return 3
    if freq == '12H':
        return 2

def year_sincos_array(n,start_date,end_date):
    start_date = pd.to_datetime(start_date)
    end_date   = pd.to_datetime(end_date)
    
    ## day distance
    first_date = pd.to_datetime('{year}-01-01'.format(year = start_date.year))
    day_of_the_year_start = (start_date - first_date).days
        
    ## year distance
    distance = (end_date - first_date).days
    
    ##
    start = (np.pi*2)*(day_of_the_year_start/365)
    end = np.pi*2*(distance/365)
    
    length = np.arange(start, end, (end-start)/n)
    df =  pd.concat([pd.Series(np.sin(length)),pd.Series(np.cos(length))],axis=1)
    df.columns = ['sin_year','cos_year']
    return df

def hour_sincos_array(hours_by_day, start_date, end_date):
    start_date = pd.to_datetime(start_date)
    end_date   = pd.to_datetime(end_date)
    ## ! year distance
    distance = (end_date - start_date).days

    start = 0
    end = np.pi*2*distance
    length = np.arange(start, end, np.pi*2/(hours_by_day))
    df =  pd.concat([pd.Series(np.sin(length)),pd.Series(np.cos(length))],axis=1)
    df.columns = ['sin_day','cos_day']
    return df.iloc[:-1]
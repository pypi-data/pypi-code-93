
import time
import pandas as pd
from functools import wraps
import logging
logging.basicConfig(level = logging.INFO)
logger = logging.getLogger()


def to_intdate(date):
    if isinstance(date,str):
        return int(''.join(date.split('-')))
    if isinstance(date,pd.Timestamp):
        return int(date.date().strftime('%Y%m%d'))
    else:
        return date
        
def get_yearlist(start_date,end_date):
    end_date = pd.Timestamp(end_date) + pd.offsets.DateOffset(years = 1)
    year_list = pd.date_range(start_date,end_date,freq="Y").to_series().dt.year.astype(str)
    return year_list

def get_yearlist(start_date,end_date):
    end_date = pd.Timestamp(end_date) + pd.offsets.DateOffset(years = 1)
    year_list = pd.date_range(start_date,end_date,freq="Y").to_series().dt.year.astype(str)
    return year_list

def print_func_time(function):
    @wraps(function)
    def func_time(*args, **kwargs):
        t0 = time.time()
        result = function(*args, **kwargs)
        t1 = time.time()
        logger.info("[In {function}][Runing Time: {time:.4f}s]".format(function = function.__name__,time = t1 - t0))
        return result
    return func_time

def bisect_right(a, x, lo=0, hi=None):
    """ Return the index where to insert item x in list a, assuming a is sorted. """

    if lo < 0:
        raise ValueError('lo must be non-negative')
    if hi is None:
        hi = len(a)
    while lo < hi:
        mid = (lo+hi)//2
        if x < a[mid]: hi = mid
        else: lo = mid+1
    return lo

def bisect_left(a, x, lo=0, hi=None):
    """ Return the index where to insert item x in list a, assuming a is sorted. """

    if lo < 0:
        raise ValueError('lo must be non-negative')
    if hi is None:
        hi = len(a)
    while lo < hi:
        mid = (lo+hi)//2
        if a[mid] < x: lo = mid+1
        else: hi = mid
    return lo

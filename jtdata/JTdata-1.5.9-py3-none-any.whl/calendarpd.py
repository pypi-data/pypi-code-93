
import os
import pandas as pd
from .config import data_path
from .tools import print_func_time,to_intdate
from .tools import bisect_left,bisect_right,to_intdate
import numpy as np

class CalendarProvider:
    
    """Calendar provider base class: Provide calendar data."""
    def __init__(self):
        self.cal_cache = {}
        self._uri_cal = os.path.join(data_path, "calendar", "{}.txt")

    def cache_cal(self,freq):
        path = self._uri_cal.format(freq)
        _calendar = np.array(self.load_calendar(freq))
        _calendar_index = {x: i for i, x in enumerate(_calendar)}  # for fast search
        self.cal_cache[freq] = (_calendar,_calendar_index)

    def load_calendar(self, freq):
        """Load original int calendar from file."""

        fname = self._uri_cal.format(freq)
        if not os.path.exists(fname):
            raise ValueError("calendar not exists for freq " + freq)
        with open(fname) as f:
            return [int(x.strip()) for x in f]

    def calendar(self, start_time=None, end_time=None, freq="Tdays"):
        _calendar, _ = self._get_calendar(freq)
        if start_time == "None":
            start_time = None
        if end_time == "None":
            end_time = None
        # strip
        if start_time:
            start_time = to_intdate(start_time)
            if start_time > _calendar[-1]:
                return np.array([])
        else:
            start_time = _calendar[0]
        if end_time:
            end_time = to_intdate(end_time)
            if end_time < _calendar[0]:
                return np.array([])
        else:
            end_time = _calendar[-1]
        si, ei = self.locate_index(start_time, end_time, freq)
        return _calendar[si : ei + 1]

    def locate_index(self, start_time, end_time, freq = 'Tdays'):
        """Locate the start time index and end time index in a calendar under certain frequency."""
        start_time = to_intdate(start_time)
        end_time = to_intdate(end_time)
        calendar, calendar_index = self._get_calendar(freq=freq)
        if start_time not in calendar_index:
            try:
                start_time = calendar[bisect_left(calendar, start_time)]
            except IndexError:
                raise IndexError(
                    "`start_time` uses a future date`"
                )
        start_index = calendar_index[start_time]
        if end_time not in calendar_index:
            end_time = calendar[bisect_right(calendar, end_time) - 1]
        end_index = calendar_index[end_time]
        return start_index, end_index

    def _get_calendar(self, freq):
        """Load calendar using memcache."""
        return self.cal_cache.get(freq)

Tdcal = CalendarProvider()
Tdcal.cache_cal('Tdays')
Tdcal.cache_cal('Adays')


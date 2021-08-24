from datetime import datetime, date

import pytest

from gpke_calendar.gpke_calendar import get_next_date, get_holiday_list, get_workdays_between
from .old_wimcal import dateList


@pytest.mark.parametrize("start , date, end", dateList)
def test_vs_wimcal_past(start, date, end):
    assert get_next_date(date, -9) == start

@pytest.mark.parametrize("start , date, end", dateList)
def test_vs_wimcal_future(start, date, end):
    assert get_next_date(date, +9) == end

def test_old_date():
    date = datetime.strptime('1970-01-01', '%Y-%m-%d')
    with pytest.raises(ValueError):
        get_next_date(date, 9)


def test_newer_than_2049_date():
    date = datetime.strptime('2050-01-01', '%Y-%m-%d')
    with pytest.raises(ValueError):
        get_next_date(date, 9)


def test_no_date():
    with pytest.raises(ValueError):
        get_next_date(None, 9)


def test_system_stand_still_day():
    assert date(2018, 1, 19) == get_next_date(date(2018, 2, 2), -9)

def test_frauentag():
    assert date(2019, 3, 11) == get_next_date(date(2019, 3, 7), 1)

def test_unique_day():
    assert(date(2020,5,8) in get_holiday_list(2020))
    assert (date(2021, 5, 8) not in get_holiday_list(2021))
    assert date(2020, 5, 11) == get_next_date(date(2020, 5, 7), 1)

def test_days_between():
    assert get_workdays_between(date(2020, 5, 8), date(2020, 5, 8)) == 0
    assert get_workdays_between(date(2020, 5, 4), date(2020, 5, 4)) == 1
    assert get_workdays_between(date(2020, 5, 8), date(2020, 5, 11)) == 1
    assert get_workdays_between(date(2020, 5, 11), date(2020, 5, 13)) == 3
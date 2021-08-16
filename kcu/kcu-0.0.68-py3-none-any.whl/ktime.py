# --------------------------------------------------------------- Imports ---------------------------------------------------------------- #

# System
from datetime import datetime
import time as builtin_time

# ---------------------------------------------------------------------------------------------------------------------------------------- #



# ---------------------------------------------------------- Public properties ----------------------------------------------------------- #

seconds_in_minute = 60
minutes_in_hour = 60
hours_in_day = 24
days_in_week = 7
days_in_year = 365 # 366
weeks_in_year = 52

seconds_in_hour = seconds_in_minute * minutes_in_hour
seconds_in_day = seconds_in_hour * hours_in_day
seconds_in_week = seconds_in_day * days_in_week
seconds_in_year = seconds_in_day * days_in_year

minutes_in_day = minutes_in_hour * hours_in_day
minutes_in_week = minutes_in_day * days_in_week
minutes_in_year = minutes_in_day * days_in_year


# ------------------------------------------------------------ Public methods ------------------------------------------------------------ #

def time(utc: bool = False) -> float:
    return datetime.utcnow().timestamp() if utc else builtin_time.time()

def today(utc: bool = False) -> int:
    return now(utc=utc).day

def time_utc() -> float:
    return time(utc=True)

def today_utc() -> int:
    return today(utc=True)

def seconds_to_time_str(seconds: float) -> str:
    hours = int(seconds/seconds_in_hour)
    seconds -= hours*seconds_in_hour

    minutes = int(seconds/seconds_in_minute)
    seconds -= minutes*seconds_in_minute

    millis = seconds - int(seconds)
    seconds = int(seconds)
    time_str = '{}:{}:{}'.format(
        str(hours).zfill(2),
        str(minutes).zfill(2),
        str(seconds).zfill(2)
    )

    if millis > 0:
        time_str += '.'

        time_str += str(int(millis*1000)).rstrip('0')

    return time_str

def time_str_to_seconds(time_str: str) -> float:
    return sum([float(c) * pow(60, i) for i, c in enumerate(reversed(time_str.split(':')))])

def is_between_hours(start_h: float, stop_h: float, utc: bool = False) -> bool:
    return is_between_seconds(start_h*seconds_in_hour, stop_h*seconds_in_hour, utc=utc)

def is_between_seconds(start_s: float, stop_s: float, utc: bool = False) -> bool:
        while start_s >= seconds_in_day:
            start_s -= seconds_in_day

        while stop_s >= seconds_in_day:
            stop_s -= seconds_in_day

        now_s = today_current_sec(utc=utc)

        if start_s < stop_s:
            return now_s >= start_s and now_s < stop_s
        elif start_s > stop_s:
            return now_s >= start_s and now_s < stop_s + seconds_in_day

        return False

def today_hours_till(h: float, utc: bool = False) -> float:
    return today_seconds_till(h*seconds_in_hour, utc=utc)/seconds_in_hour

def today_seconds_till(s: float, utc: bool = False) -> float:
    now_s = today_current_sec(utc=utc)

    if s >= now_s:
        return s - now_s

    return seconds_in_day - now_s + s

def hours_till(h: float, utc: bool = False) -> float:
    return seconds_till(h*seconds_in_hour, utc=utc)/seconds_in_hour

def seconds_till(s: float, utc: bool = False) -> float:
    return s - time(utc=utc)

def today_current_hour(utc: bool = False) -> float:
    return today_current_sec(utc=utc) / seconds_in_hour

def today_current_sec(utc: bool = False) -> float:
    _now = now(utc)

    return _now.hour*seconds_in_hour + _now.minute*seconds_in_minute + _now.second

def now(utc: bool = False):# -> datetime:
    return datetime.utcnow() if utc else datetime.now()

# ---------------------------------------------------------------------------------------------------------------------------------------- #
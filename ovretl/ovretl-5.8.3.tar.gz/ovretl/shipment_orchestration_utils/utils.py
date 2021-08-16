from datetime import datetime, date, timedelta


def get_days_from_timedelta(delta: timedelta):
    return delta.days


def set_negative_to_zero(a: float):
    if a < 0:
        return 0
    else:
        return a


def datetime_to_date(dt: datetime) -> date:
    return dt.date()


def string_date_to_datetime(datestr):
    try:
        return datetime.strptime(datestr, "%Y-%m-%dT%H:%M:%S.%fZ").date()
    except:
        return None

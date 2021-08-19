import logging
from copy import deepcopy
from datetime import datetime, timedelta
from logging import Logger
from typing import Any, Dict, List, Optional

import dateparser
import holidays.countries.united_states
import pytz
from dateutil import parser

BASE_TZ = pytz.timezone(zone="US/Eastern")
UPDATED_AT: str = "updated_at"
CREATED_AT: str = "created_at"
GRAINS: List[str] = ["days", "hours", "minutes", "seconds"]


def date_time_format() -> str:
    return "%Y%m%dT%H%M"


def to_est() -> datetime:
    return datetime.now(tz=BASE_TZ)


def tz_localize(a_date: datetime) -> datetime:
    return BASE_TZ.localize(a_date)


def date_parse(date_str: str) -> Optional[datetime]:
    if date_str is None:
        return None

    try:
        return dateparser.parse(date_str)
    except Exception as e:
        logging.getLogger("").exception(
            f"Date input of {date_str} unable to be parsed by default parser. Falling back to default parser: {e}."
        )
        return parser.isoparse(date_str)


def to_date(date_str: str, format_str: str = "%Y%m%d") -> datetime:
    return datetime.strptime(date_str, format_str)


def date_to_str(a_date: datetime = to_est(), format_str: str = "%Y%m%d") -> str:
    """Provides a day representation.

    Returns:
        A year, month, and day string
    """
    return a_date.strftime(format_str)


def str_to_iso_8601(a_str: str, format_str: str = "%Y-%m-%d %H:%M:%S.%f") -> datetime:
    return datetime.strptime(a_str, format_str)


def str_to_datetime(a_str: str = to_est(), format_str: str = date_time_format()) -> datetime:
    return datetime.strptime(a_str, format_str)


def datetime_to_str(a_date: datetime = to_est(), format_str: str = date_time_format()) -> Optional[str]:
    """Provides a minute representation.

    Returns:
        A year, month, day, hour, minute string
    """
    if a_date is None:
        return None

    return a_date.isoformat()


def second_to_str(a_date: datetime = to_est(), format_str: str = "%Y%m%d%H%M%S") -> str:
    """Provides a second representation.

    Returns:
        A year, month, day, hour, minute, second string
    """
    return a_date.strftime(format_str)


def time_to_str(a_date: datetime = to_est(), format_str: str = "%H%M") -> str:
    """Provides a time string based representation.

    Args:
        a_date: a date
        format_str: time format string

    Returns:
        A hour, minute string
    """
    return a_date.strftime(format_str)


def str_to_time(time_str: str, format_str: str = "%H%M") -> datetime:
    """Provides a time from a string based representation.

    Args:
        time_str: time string
        format_str: time format string

    Returns:
        A parsed time
    """
    return datetime.strptime(time_str, format_str)


def readable_datetime_to_str(a_date: datetime = to_est(), format_str: str = "%Y-%m-%d %H:%M:00") -> str:
    """Provides a minute representation.

    Returns: a formatted string, defaults to year, month, day, hour, minute string
    """
    return a_date.strftime(format_str)


def readable_date_to_str(a_date: datetime = to_est(), format_str: str = "%Y-%m-%d") -> str:
    """Provides a minute representation.

    Returns: a year, month, day
    """
    return a_date.strftime(format_str)


def time_offset(seconds: int, a_datetime=to_est()) -> datetime:
    """Offset in seconds from a time.

    Args:
        seconds: seconds to offset
        a_datetime: time

    Returns: offset time
    """
    return a_datetime - timedelta(seconds=seconds)


def time_offset_in_days(days: int, a_datetime=to_est()) -> datetime:
    """Offset in days from a time.

    Args:
        days: days to offset
        a_datetime: time

    Returns: offset time
    """
    return a_datetime - timedelta(days=days)


def timeoffset_as_str(seconds: int, a_datetime=to_est()) -> str:
    """Provides a minute representation.

    Returns: a year, month, day, hour, minute string
    """
    return time_to_str(time_offset(seconds=seconds, a_datetime=a_datetime))


def timestamp_strs_for_window(
    window: int,
    seconds: int,
    a_datetime: datetime = to_est(),
) -> List[str]:
    """For a start time, num of windows and length per window, produce time strings from start time to
    start time - (window * seconds).

    Args:
        window: num intervals
        seconds: num window seconds
        a_datetime: time

    Returns: list of times descending from a start time to the past.
    """
    return [timeoffset_as_str(seconds=r * seconds, a_datetime=a_datetime) for r in range(window)]


def floor_sec_timestamp(a_time: datetime = to_est(), second_granularity: int = 10) -> datetime:
    return a_time - timedelta(seconds=a_time.second % second_granularity)


def time_floor(a_date: datetime = to_est(), window: int = 10) -> datetime:
    return a_date - timedelta(minutes=a_date.minute % window, seconds=a_date.second, microseconds=a_date.microsecond)


def convert_dates(input_data: Dict[str, Any], *args: str) -> Dict[str, Any]:
    all_keys: List[str] = [*args, UPDATED_AT, CREATED_AT]

    if any(k in input_data for k in all_keys):
        data: Dict[str, Any] = deepcopy(input_data)

        for key in all_keys:
            if key in input_data:
                data[key] = date_parse(data[key])

        return data

    return input_data


def is_holiday(a_time: datetime = to_est(), format_str: str = "%Y-%m-%d", logger: Optional[Logger] = None) -> bool:
    if logger:
        logger.info(
            f"is_holiday: {a_time} - "
            + f"{True if a_time.strftime(format_str) in holidays.countries.united_states.US() else False}"
        )
    return True if a_time.strftime(format_str) in holidays.countries.united_states.US() else False


def is_weekend(a_time: datetime = to_est(), logger: Optional[Logger] = None) -> bool:
    if logger:
        logger.info(
            f"is_weekend: {a_time} - {True if a_time.date().weekday() > 4 else False}"
        )
    return True if a_time.date().weekday() > 4 else False


def _maybe_singleize(plural_grain: str, value: int) -> str:
    """If the value is 1, then toss the plural s at the end of the granularity.

    Args:
        plural_grain: grain name
        value: value

    Returns: either the initial grain name, or a singular version
    """
    if value == 1:
        return plural_grain[:-1]

    return plural_grain


def to_readable_duration(delta: timedelta) -> Optional[str]:
    """Converts a timedelta to a readable duration string, e.g. "X days, Y hours, Z minutes, A seconds"

    Args:
        delta: time delta (timeA - timeB)

    Returns: readable string based on the duration
    """
    days: int = delta.days
    seconds: int = delta.seconds

    hours: int = seconds // 3600

    remaining: int = seconds - hours * 3600
    mins: int = remaining // 60
    secs: int = remaining - mins * 60

    combined = [
        f"{data[1]} {_maybe_singleize(data[0], data[1])}"
        for data in zip(GRAINS, [days, hours, mins, secs])
        if data[1] > 0
    ]

    if len(combined) <= 0:
        return None

    return ", ".join(combined)


# if __name__ == "__main__":
#     print(datetime_to_str())
#     print(convert_dates({'a': '2018-02-01'}, 'a'))
#
#     date_str = "Mon, 15 Mar 2021 19:07:17 GMT"
#
#     print(dateparser.parse(date_str))

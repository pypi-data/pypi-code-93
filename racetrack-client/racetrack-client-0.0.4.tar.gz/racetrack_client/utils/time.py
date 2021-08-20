from datetime import datetime, timezone

import pytz


def datetime_to_timestamp(dt: datetime) -> int:
    """Convert datetime.datetime to integer timestamp in seconds"""
    return int(dt.timestamp())


def timestamp_to_datetime(timestamp: int) -> datetime:
    """Convert integer timestamp in seconds to datetime.datetime"""
    return datetime.fromtimestamp(timestamp, tz=timezone.utc)


def datetime_to_str(dt: datetime) -> str:
    return dt.strftime('%Y-%m-%d %H:%M:%S %z')


def now() -> datetime:
    """Return current datetime with UTC timezone set"""
    return datetime.now(tz=pytz.UTC)

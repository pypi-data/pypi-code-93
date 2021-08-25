from datetime import timedelta, datetime, timezone, tzinfo


def rfc3339_format(dt: datetime) -> str:
    return dt.astimezone().isoformat()


def milliseconds(delta: timedelta) -> int:
    return int(delta.total_seconds() * 1000.0)

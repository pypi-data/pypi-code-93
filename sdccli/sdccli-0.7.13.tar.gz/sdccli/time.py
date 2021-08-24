from datetime import datetime, timedelta

from dateutil.parser import parse


def date_range_in_sec(start, end, duration=None):
    if not duration:
        duration = '1D'

    duration_secs = duration_to_seconds(duration)
    to_sec = parse(end).timestamp() if end else 0
    from_sec = parse(start).timestamp() if start else 0

    if not from_sec and not to_sec:
        to_sec = (datetime.utcnow() - datetime.utcfromtimestamp(0)).total_seconds()

    if from_sec > to_sec:
        raise IndexError("The start date is after the end date: {} <-> {}".format(parse(start), parse(end)))

    from_sec = from_sec if from_sec else to_sec - duration_secs
    to_sec = to_sec if to_sec else from_sec + duration_secs
    return from_sec, to_sec


def duration_to_timedelta(duration):
    return timedelta(seconds=(duration_to_seconds(duration)))


def duration_to_seconds(duration):
    format_error = "Error: duration needs to be in the form of <num><units> where <units> can be: S, M, H, D or W. (ex: 30M, 1H, 3D, 2W)"
    unit_sec = {
        "s": 1,
        "m": 60,
        "h": 60 * 60,
        "d": 60 * 60 * 24,
        "w": 60 * 60 * 24 * 7
    }
    if duration[-1].lower() not in unit_sec.keys():
        print(format_error)
        return None

    try:
        return int(duration[:-1]) * unit_sec[duration[-1].lower()]
    except ValueError:
        print(format_error)
    return None


def format_timestamp(timestamp):
    return str(datetime.utcfromtimestamp(timestamp / 10 ** 3))

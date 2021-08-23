import time
from datetime import time as dttime, timedelta, datetime


def str_parse_to_time(date_str, formats=None):
    formats = formats or ('%H:%M:%S', '%H:%M',
                          '%I:%M:%S%p', '%I:%M%p',
                          '%I:%M:%S %p', '%I:%M %p')
    if date_str and date_str != "None" and date_str.strip():
        for format in formats:
            try:
                timetuple = time.strptime(date_str, format)
                return dttime(timetuple.tm_hour,
                              timetuple.tm_min,
                              timetuple.tm_sec)
            except ValueError:
                pass

        raise ValueError('Invalid time format: %s' % date_str)
    return


def is_between_time(now, time_begin, time_end):
    today = now.replace(hour=0, minute=0, second=0)

    dt_begin = datetime.combine(today, time_begin, now.tzinfo)

    if time_begin > time_end:
        tomorrow = today + timedelta(days=1)
        dt_end = datetime.combine(tomorrow, time_end, now.tzinfo)
        diff_for_dt_end = dt_end - dt_begin

        if time_begin > now.time() and now.time() < time_end:
            yesterday = today - timedelta(days=1)
            dt_begin = datetime.combine(yesterday, time_begin, now.tzinfo)
            dt_end = dt_begin + diff_for_dt_end
    else:
        dt_end = datetime.combine(today, time_end, now.tzinfo)

    return now > dt_begin and now < dt_end

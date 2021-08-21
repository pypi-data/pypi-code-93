from __future__ import annotations

import time
from datetime import time as dttime


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

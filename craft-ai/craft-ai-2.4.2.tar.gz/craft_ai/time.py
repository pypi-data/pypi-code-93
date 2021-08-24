# To avoid conflicts between python's own 'time' and this 'time.py'
# cf. https://stackoverflow.com/a/28854227
from __future__ import absolute_import

import time

from datetime import datetime, tzinfo, timedelta

from pytz import utc as pyutc
from tzlocal import get_localzone
from dateutil.parser import isoparse

from craft_ai.errors import CraftAiTimeError
from craft_ai.timezones import is_timezone, timezone_offset_in_sec

_EPOCH = datetime(1970, 1, 1, tzinfo=pyutc)


class Time(object):
    """Handles time in a useful way for craft ai's client"""

    def __init__(self, t=None, timezone=None):
        def time_from_datetime_timestamp_and_timezone(timestamp, timezone):
            # Handle when datetime already provides timezone :
            # datetime(2012, 9, 12, 6, 0, 0, tzinfo=pytz.utc)
            result = timestamp
            if (result.tzinfo is None) and (not timezone):
                # Handle this format :
                # Time(datetime(2011, 1, 1, 0, 0), timezone=None)
                raise CraftAiTimeError("You must provide at least one timezone")
            elif (result.tzinfo is None) and timezone:
                # Handle this format :
                # Time(datetime(2011, 1, 1, 0, 0), timezone="+02:00")
                result = pyutc.localize(result)
                result = set_timezone(result, timezone)
            elif (result.tzinfo is not None) and (timezone):
                # Handle format like :
                # Time(datetime(2002, 10, 27, 6, 0, 0, tzinfo=utc),timezone="+02:00" )
                raise CraftAiTimeError(
                    "You must provide one timezone, but two were provided:"
                    " in the datetime and in the timezone parameter."
                )
            return result

        def time_from_string_timestamp_and_timezone(timestamp, timezone):
            # Else if t is a string we try to interprete it as an ISO time
            # string
            try:
                # Can't use strptime with %z in Python 2
                # https://stackoverflow.com/a/23940673
                result = isoparse(timestamp)
            except ValueError as e:
                raise CraftAiTimeError(
                    """Unable to instantiate Time from given string. {}""".format(
                        e.__str__()
                    )
                )

            if result.tzinfo is None:
                # Handle format like : Time(t="2017-01-01 00:00:00")
                if timezone:
                    # Handle format like : Time(t="2017-01-01 00:00:00", timezone="-03:00")
                    result = pyutc.localize(result)
                    result = set_timezone(result, timezone)
                else:
                    raise CraftAiTimeError(
                        "The given datetime string must be tz-aware,"
                        " or you must provide an explicit timezone."
                    )
            else:
                if timezone:
                    # Handle format like : Time("2011-04-22 01:00:00+0900", timezone="-03:00")
                    raise CraftAiTimeError(
                        "You must provide one timezone, but two were provided:"
                        " in the datetime string and in the timezone parameter."
                    )
            return result

        def set_time_and_timezone(timestamp, timezone):
            if timestamp is None:
                # If no initial timestamp is given, the current local time is used
                _time = datetime.now(get_localzone())
                # If a timezone is specified we can try to use it
                if timezone:
                    # Handle theses cases :   Time(timezone="+01:00") & Time(timezone="CET")
                    _time = set_timezone(_time, timezone)

            elif isinstance(timestamp, int):
                # Else if t is an int we try to use it as a given timestamp with
                # local UTC offset by default .
                try:
                    # Handle format like  : Time().timezone
                    _time = datetime.fromtimestamp(timestamp, get_localzone())
                except (OverflowError, OSError) as e:
                    raise CraftAiTimeError(
                        """Unable to instantiate Time from given timestamp. {}""".format(
                            e.__str__()
                        )
                    )
                # If a timezone is specified we can try to use it
                if timezone:
                    # Handle this type of datetime format : Time(1356998400, timezone="+0100")
                    _time = set_timezone(_time, timezone)

            elif isinstance(timestamp, datetime):
                _time = time_from_datetime_timestamp_and_timezone(timestamp, timezone)

            elif isinstance(timestamp, str):
                _time = time_from_string_timestamp_and_timezone(timestamp, timezone)

            else:
                raise CraftAiTimeError(
                    """Unable to instantiate Time from given timestamp."""
                    """ It must be integer or string."""
                )
            return _time

        def set_timezone(timestamp, timezone):
            if isinstance(timezone, tzinfo):
                # If it's already a timezone object, no more work is needed
                _time = timestamp.astimezone(timezone)
            elif is_timezone(timezone):
                # If it's a string, we convert it to a usable timezone object
                offset = timezone_offset_in_sec(timezone)
                _time = timestamp.astimezone(tz=dt_timezone(timedelta(seconds=offset)))
            else:
                raise CraftAiTimeError(
                    """Unable to instantiate Time with the given timezone."""
                    """ {} is neither a string nor a timezone.""".format(timezone)
                )
            return _time

        _time = set_time_and_timezone(t, timezone)

        try:
            self.utc_iso = _time.isoformat()
        except ValueError as e:
            raise CraftAiTimeError(
                """Unable to create ISO 8061 UTCstring. {}""".format(e.__str__())
            )

        self.day_of_week = _time.weekday()
        self.time_of_day = _time.hour + _time.minute / 60 + _time.second / 3600
        self.day_of_month = _time.day
        self.month_of_year = _time.month
        self.timezone = _time.strftime("%z")[:3] + ":" + _time.strftime("%z")[3:]
        self.timestamp = Time.timestamp_from_datetime(_time)

    def to_dict(self):
        """Returns the Time instance as a usable dictionary for craft_ai"""
        return {
            "timestamp": int(self.timestamp),
            "timezone": self.timezone,
            "time_of_day": self.time_of_day,
            "day_of_week": self.day_of_week,
            "day_of_month": self.day_of_month,
            "month_of_year": self.month_of_year,
            "utc_iso": self.utc_iso,
        }

    @staticmethod
    def timestamp_from_datetime(date_time):
        """Returns POSIX timestamp as float"""
        if date_time.tzinfo is None:
            return (
                time.mktime(
                    (
                        date_time.year,
                        date_time.month,
                        date_time.day,
                        date_time.hour,
                        date_time.minute,
                        date_time.second,
                        -1,
                        -1,
                        -1,
                    )
                )
                + date_time.microsecond / 1e6
            )
        return (date_time - _EPOCH).total_seconds()


# pylint: disable=C0103,W0212
class dt_timezone(tzinfo):
    """
    timezone class from python's standard library datetime
    This is reincluded here to ensure compatibility with python
    versions earlier than 3.2.
  """

    __slots__ = "_offset", "_name"

    # Sentinel value to disallow None
    _Omitted = object()

    def __new__(cls, offset, name=_Omitted):
        if not isinstance(offset, timedelta):
            raise TypeError("offset must be a timedelta")
        if name is cls._Omitted:
            if not offset:
                return cls.utc
            name = None
        elif not isinstance(name, str):
            raise TypeError("name must be a string")
        if not cls._minoffset <= offset <= cls._maxoffset:
            raise ValueError(
                "offset must be a timedelta"
                " strictly between -timedelta(hours=24) and"
                " timedelta(hours=24)."
            )
        if offset.microseconds != 0 or offset.seconds % 60 != 0:
            raise ValueError(
                "offset must be a timedelta" " representing a whole number of minutes"
            )
        return cls._create(offset, name)

    @classmethod
    def _create(cls, offset, name=None):
        self = tzinfo.__new__(cls)
        self._offset = offset
        self._name = name
        return self

    def __getinitargs__(self):
        """pickle support"""
        if self._name is None:
            return (self._offset,)
        return (self._offset, self._name)

    def __eq__(self, other):
        return self._offset == other._offset

    def __hash__(self):
        return hash(self._offset)

    def __repr__(self):
        """Convert to formal string, for repr().

    >>> tz = dt_timezone.utc
    >>> repr(tz)
    "datetime.dt_timezone.utc"
    >>> tz = dt_timezone(timedelta(hours=-5), 'EST')
    >>> repr(tz)
    "datetime.dt_timezone(datetime.timedelta(-1, 68400), 'EST')"
    """
        if self is self.utc:
            return "datetime.dt_timezone.utc"
        if self._name is None:
            return "%s(%r)" % ("datetime." + self.__class__.__name__, self._offset)
        return "%s(%r, %r)" % (
            "datetime." + self.__class__.__name__,
            self._offset,
            self._name,
        )

    def __str__(self):
        return self.tzname(None)

    def utcoffset(self, dt):
        if isinstance(dt, datetime) or dt is None:
            return self._offset
        raise TypeError("utcoffset() argument must be a datetime instance" " or None")

    def tzname(self, dt):
        if isinstance(dt, datetime) or dt is None:
            if self._name is None:
                return self._name_from_offset(self._offset)
            return self._name
        raise TypeError("tzname() argument must be a datetime instance" " or None")

    def dst(self, dt):
        if isinstance(dt, datetime) or dt is None:
            return None
        raise TypeError("dst() argument must be a datetime instance" " or None")

    def fromutc(self, dt):
        if isinstance(dt, datetime):
            if dt.tzinfo is not self:
                raise ValueError("fromutc: dt.tzinfo " "is not self")
            return dt + self._offset
        raise TypeError("fromutc() argument must be a datetime instance" " or None")

    _maxoffset = timedelta(hours=23, minutes=59)
    _minoffset = -_maxoffset

    @staticmethod
    def _name_from_offset(delta):
        if delta < timedelta(0):
            sign = "-"
            delta = -delta
        else:
            sign = "+"
        hours, rest = divmod(delta, timedelta(hours=1))
        minutes = rest // timedelta(minutes=1)
        return "UTC{}{:02d}:{:02d}".format(sign, hours, minutes)


dt_timezone.utc = dt_timezone._create(timedelta(0))
dt_timezone.min = dt_timezone._create(dt_timezone._minoffset)
dt_timezone.max = dt_timezone._create(dt_timezone._maxoffset)
# pylint: enable=C0103,W0212

# pylint: enable=import-self,ungrouped-imports,wrong-import-order,no-member

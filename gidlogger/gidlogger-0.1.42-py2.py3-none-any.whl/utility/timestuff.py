from pytz import timezone as pytz_timezone, common_timezones, common_timezones_set, country_names, all_timezones, all_timezones_set, country_timezones
from enum import Enum, unique, auto, Flag
from pprint import pprint
from typing import Any, Iterable, Callable, Union, Optional
import os


class QuickTimezone:
    GERMANY = pytz_timezone("Europe/Berlin")
    LONDON = pytz_timezone("Europe/London")
    MOSCOW = pytz_timezone("Europe/Moscow")
    US_PACIFIC = pytz_timezone("US/Pacific")
    US_EASTERN = pytz_timezone("US/Eastern")
    US_CENTRAL = pytz_timezone("US/Central")

    @classmethod
    def get(cls, key: str, default: Optional[Any] = None):
        mod_key = key.upper()
        _out = getattr(cls, mod_key, None)
        if _out is None:
            new_mod_key = f"US_{mod_key}"
            _out = getattr(cls, new_mod_key, None)
        if _out is None:
            return default
        return _out


if __name__ == "__main__":
    pass

#!/usr/bin/env python3
""" Smart date/time parsing """

import datetime as dt
from enum import Enum
import re
from typing import Optional, List, Tuple

from work_components import consts, util


class RoundingMode(Enum):
    NONE = 0
    DOWN = 1
    UP = 2


# time resolution and parsing #


def resolve_time_argument(
    argument: str, baseline_date: dt.date, rounding_mode: RoundingMode
) -> dt.datetime:
    """ Parse the input to the time argument. Important: This function only understands mode-agnostic times. """

    if argument == "now":
        baseline_time = dt.datetime.now().replace(second=0, microsecond=0).time()
        baseline_datetime = dt.datetime.combine(baseline_date, baseline_time)
        return round_time(baseline_datetime, rounding_mode)

    parsed_time = parse_time_str(argument)
    return dt.datetime.combine(baseline_date, parsed_time)


def round_time(
    baseline_datetime: dt.datetime, rounding_mode: RoundingMode, buckets: int = 15
) -> dt.datetime:
    """
    Round the given baseline_datetime based on the given rounding_mode.

    Keyword arguments:
    - baseline_time : The baseline (datetime object)
    - mode          : start (down) or stop (up)
    - buckets       : time buckets to round to (default=15)
    """

    if buckets is not None and (buckets < 1 or buckets > 60):
        raise ValueError(f"buckets expected to be in range [1, 60]; got: {buckets}")

    modulo_min = baseline_datetime.minute % buckets

    # Time is already rounded / no rounding specified
    if modulo_min == 0 or rounding_mode == RoundingMode.NONE:
        return baseline_datetime

    offset = dt.timedelta(minutes=-modulo_min)

    # We have currently rounded down; to round up, add exactly one bucket
    if rounding_mode == RoundingMode.UP:
        offset += dt.timedelta(minutes=buckets)

    return baseline_datetime + offset


def parse_time_str(argument: str) -> dt.time:
    """
    Return the time corresponding to the given string.
    Possible inputs:
    - 1:1 / 12:30 / 15:9 (%H:%M)
    - 2 / 19 / 23 (%H)
    """

    if re.fullmatch(r"\d{1,2}", argument):
        argument += ":00"

    if re.fullmatch(r"\d{4}", argument):
        argument = f"{argument[0:2]}:{argument[2:4]}"

    match = re.fullmatch(r"(\d{1,2}):(\d{1,2})", argument)

    if not match:
        raise ValueError('Invalid time string "' + argument + '" given; see --help')

    hour = int(match.group(1))
    minute = int(match.group(2))

    return dt.time(hour=hour, minute=minute)


# date resolution and parsing #


def resolve_date_argument(argument: str) -> dt.date:
    """ Parse the input to the date argument. """

    if "today".startswith(argument):
        return dt.date.today()
    elif "yesterday".startswith(argument):
        return dt.date.today() - dt.timedelta(days=1)

    return parse_date_str(argument)


def resolve_day_argument(argument: str) -> dt.date:
    """ Parse the input to the day argument. """
    if not argument:
        raise ValueError("Empty day argument is not parseable.")

    today: dt.date = dt.date.today()
    last_seven_days: List[dt.date] = util.get_period(
        period_start=today - dt.timedelta(days=6), period_end=today
    )
    indices: List[int] = [d.weekday() for d in last_seven_days]
    day_names: List[str] = [d.lower() for d in consts.WEEKDAYS]
    # Build a list of the last seven weekday names in the order they appeared (ending today).
    day_names = [day_names[i] for i in indices]

    match: Tuple[int, float] = (0, 0.0)
    argument = argument.lower()
    for day_name in day_names:
        # Full match
        if argument == day_name:
            match = (day_names.index(day_name), 1.0)
            break
        # Partial match, e. g. "mon" for "monday" -> 50 %
        elif day_name.startswith(argument):
            new_match = len(day_name) / len(argument)
            if new_match > match[1]:
                match = (day_names.index(day_name), new_match)
    if match[1] == 0.0:
        raise ValueError("Given argument does not match anything")

    # Match with weekday with same index
    day_index = match[0]
    return last_seven_days[day_index]


def parse_date_str(argument: str) -> dt.date:
    """
    Return the date corresponding to the given string.
    Possible inputs:
    - 12. (%d.)
    - 1.1. / 12.02. (%d.%m.)
    - 25.2.19 / 9.9.20 (%d.%m.%y)

    When no year is given, the current year is assumed.
    """

    # Match groups: 1 = day, 2 = month + year, 3 = month, 4 = year
    date_pattern = r"(\d{1,2})\.((\d{1,2})\.(\d{2}|\d{4})?)?"

    match = re.fullmatch(date_pattern, argument)
    if not match:
        raise ValueError(f'The date string "{argument}" can\'t be parsed; see --help.')

    day = int(match.group(1))

    # The month and year might not be given; in that case we use the current one
    today = dt.date.today()

    given_month: Optional[str] = match.group(3)
    month = int(given_month) if given_month is not None else today.month
    given_year: Optional[str] = match.group(4)
    year: int = today.year
    if given_year is not None:
        if len(given_year) == 2:
            given_year = f"20{given_year}"
        year = int(given_year)

    return dt.date(year=year, month=month, day=day)

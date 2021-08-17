#!/usr/bin/env python3

""" Utils for the work module. """

import datetime as dt
from collections import Counter
import re
from typing import List, Optional


def verify_date_arguments(
    year: Optional[int], month: Optional[int] = None, day: Optional[int] = None
):
    """ Ensure only the allowed combinations are set and all values are valid. """

    if year is None and month is None and day is None:
        return

    if year is None or (month is None and day is not None):
        raise ValueError("Invalid combination of year, month and day")

    month = month or 1
    day = day or 1
    # datetime verifies the validity of the given date
    dt.datetime(year, month, day)


def minutes_difference(start: dt.datetime, end: dt.datetime) -> float:
    """ Calculates the minutes between start and end time. If end < start the result is negative! """
    return (end - start) / dt.timedelta(minutes=1)


def get_period(period_start: dt.date, period_end: dt.date) -> List[dt.date]:
    """
    Return a period defined by two dates.

    The order of start and end does not influence the result.
    """

    period_ends: List[dt.date] = sorted([period_start, period_end])
    start_day, end_day = period_ends

    period: List[dt.date] = []
    iterated_day = start_day
    while iterated_day <= end_day:
        period.append(iterated_day)
        iterated_day += dt.timedelta(days=1)

    return period


class Color(object):
    """ See https://en.wikipedia.org/wiki/ANSI_escape_code#8-bit """

    BLUE = 27
    GRAY = 242
    GREEN = 34
    ORANGE = 202
    RED = 9

    @staticmethod
    def color(text: str, clr_code: int, bg: bool = False) -> str:
        fg_bg_code = "38" if not bg else "48"
        return Color._format(
            text=text, format_code="{};5;{}".format(fg_bg_code, clr_code)
        )

    @staticmethod
    def bold(text: str) -> str:
        return Color._format(text=text, format_code="1")

    @staticmethod
    def _format(text: str, format_code: str) -> str:
        return "\x1b[{}m{}\x1b[0m".format(format_code, text)

    # TODO add tests
    @staticmethod
    def clear(text: str) -> str:
        """Clear any applied color codes from the text."""
        return re.sub(r"\x1b\[[0-?]*[ -\/]*[@-~]", "", text)


class PrinTable:
    def __init__(self) -> None:
        self.rows: List[List[str]] = []
        self.col_widths: Counter = Counter()

    def add_row(self, row: List[str]) -> None:
        self.rows.append(row)
        for i, col in enumerate(row):
            # Clear the col of color codes before computing the string length
            self.col_widths[i] = max(self.col_widths[i], len(Color.clear(col)))

    def printable(self) -> List[List[str]]:
        """ Return rows with each cell left-justified to match the column width. """
        result: List[List[str]] = []
        for row in self.rows:
            result.append([])
            for i, col in enumerate(row):
                result[-1].append(col.ljust(self.col_widths[i]))
        return result

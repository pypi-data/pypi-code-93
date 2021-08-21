"""For all your time handeling needs, here it is."""

from datetime import datetime
import time
import re


def extract_date(date):
    """Make datetime object from string.

    Args:
        date (str): A string in either ISO, epoch, or predefined format

    Raises:
        ValueError: Raised when none of the formats are right.

    Returns:
        datetime.datetime: Python datetime format.
    """
    num_format = re.compile("^[\-]?[1-9][0-9]*\.?[0-9]+$")

    # all the formats the date might be in
    POSSIBLE_DATE_FORMATS = ['%m/%d/%Y', '%Y/%m/%d', "%Y-%m-%dT%H:%M:%S.%fZ"]

    for date_format in POSSIBLE_DATE_FORMATS:
        try:
            return datetime.strptime(date, date_format)  # try to get the date
        except ValueError:
            pass  # if incorrect format, keep trying other formats

    # Check if it's a usable epoch format.
    if num_format.search(date):
        try:
            return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(date)))
        except ValueError:
            raise ValueError(f"{date} was not in one of the approved formats.")
    else:
        # Last resort => ISO format
        try:
            return datetime.fromisoformat(date)
        except:
            raise ValueError(f"{date} was not in one of the approved formats.")
    raise ValueError(f"{date} was not in one of the approved formats.")


def filterTimeStamps(relations, filterType: str, **kwargs):
    """Filter dates by their timestamps.

    Args:
        relations (List[Relationship, ...]): List containing the Relationship
            pydantic dataclass. (see dataStructures.py for dataclass definition)
        filterType (str): Information on how to filter.
            Can be ["betweenWeeks", "inWeek", "betweenDates", "all"]
        kwargs (dict): Provide {"begin": val, "end": val} in week numbers or
             dates for "betweenWeeks" or "betweenDates" respectively. And provide
             {"week": val} for "inWeek" to filter all in that specific week.

    Returns:
        List[Relationships, ...]: List of relationships objects that fall within
            a predefined timeframe.
    """
    if filterType == "betweenWeeks":
        return ([
            i for i in relations
            if kwargs["begin"] < i.week < kwargs["end"]
        ])
    elif filterType == "inWeek":
        return ([
            i for i in relations if kwargs["week"] == i.week
        ])
    elif filterType == "betweenDates":
        return ([
            i for i in relations if extract_date(kwargs["begin"])
            < i.r_timestamp < extract_date(kwargs["end"])
        ])
    elif filterType == "all":
        return relations

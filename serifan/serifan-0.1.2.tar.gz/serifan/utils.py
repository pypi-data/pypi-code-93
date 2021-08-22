from datetime import date
from datetime import datetime as dt
from typing import List


def list_strings_to_dates(lst) -> List[date]:
    # One of the string dates in the api has a period at the end.
    return [dt.strptime(d.strip("."), "%Y-%m-%d").date() for d in lst["dates"]]

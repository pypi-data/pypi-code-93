"""All commonly used pydantic network dataclasses ready for reuse."""

from typing import List, Optional
from datetime import datetime
import time
import re

from pydantic import BaseModel, validator, Extra

import numpy as np


class Relationship(BaseModel):
    """Dataclass for a single relationship."""

    r_from: str
    r_to: str
    r_timestamp: datetime
    r_type: Optional[str]
    r_strength: Optional[int]

    class Config:
        """Configure dataclass."""

        extra = Extra.allow

    @validator("r_timestamp", pre=True)
    def time_validate(cls, v):
        """Make sure that the date type formatting works out.

        Parameters
        ----------
        v :
            

        Returns
        -------

        """
        num_format = re.compile("^[\-]?[1-9][0-9]*\.?[0-9]+$")

        # all the formats the date might be in
        POSSIBLE_DATE_FORMATS = ['%m/%d/%Y', '%Y/%m/%d', "%Y-%m-%dT%H:%M:%S.%fZ"]

        for date_format in POSSIBLE_DATE_FORMATS:
            try:
                return datetime.strptime(v, date_format)  # try to get the date
            except ValueError:
                pass  # if incorrect format, keep trying other formats

        # Check if it's numerical
        if num_format.search(v):
            try:
                return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(v)))
            except ValueError:
                raise ValueError(f"{v} was not in one of the approved formats.")
        else:
            # Last resort => ISO format
            try:
                return datetime.fromisoformat(v)
            except ValueError:
                raise ValueError(f"{v} was not in one of the approved formats.")
        raise ValueError(f"{v} was not in one of the approved formats.")

    @property
    def week(self):
        """ """
        return self.r_timestamp.isocalendar().week

    @property
    def year(self):
        """ """
        return self.r_timestamp.isocalendar().year


class RelationshipData(BaseModel):
    """Encoding all relationships in a dataset."""

    relations: List[Relationship]

    @property
    def active_weeks(self):
        """Get distinct weeks of activity."""
        return np.unique([m.week for m in self.relations])

    @property
    def active_years(self):
        """Get distinct weeks of activity."""
        return np.unique([m.year for m in self.relations])

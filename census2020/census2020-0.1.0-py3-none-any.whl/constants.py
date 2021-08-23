"""
Package-level constants
"""
from strenum import StrEnum


class SummaryLevel(StrEnum):
    """
    Values for the SUMLEV column in PL94 data
    """

    STATE = "040"
    STATE_COUNTY = "050"
    STATE_COUNTY_TRACT = "140"
    STATE_COUNTY_TRACT_BLOCKGROUP = "150"
    STATE_COUNTY_TRACT_BLOCKGROUP_BLOCK = "750"

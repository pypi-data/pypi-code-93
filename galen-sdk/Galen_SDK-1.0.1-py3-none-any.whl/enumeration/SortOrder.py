"""
SortOrder Enum Class
"""

from enum import Enum


class SortOrder (Enum):
    ASC = 1
    DESC = 2

    @staticmethod
    def to_string(sort_order):
        """
        Helper function for SDK
        :param sort_order: takes in a SortOrder Enum
        :return: a string that represents that enum
        """
        if sort_order == SortOrder.ASC:
            return "ASC"
        if sort_order == SortOrder.DESC:
            return "DESC"

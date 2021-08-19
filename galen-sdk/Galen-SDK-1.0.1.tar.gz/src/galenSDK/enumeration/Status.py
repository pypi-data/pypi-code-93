"""
Status Enum Class
"""

from enum import Enum


class Status(Enum):
    Active = 1
    Inactive = 2
    Pending = 3

    @staticmethod
    def to_string(status) -> str:
        """
        Helper function that parses a string into a status enum
        :param status: status enum that will be converted to string
        """
        if status is None:
            return None
        if status == Status.Active:
            return "Active"
        if status == Status.Inactive:
            return "Inactive"
        if status == Status.Pending:
            return "Pending"
        return None

    @staticmethod
    def string_to_status(string_status: str):
        """
        Helper function that parses string into a status enum
        :param string_status: string that will be converted to Status Enum
        """
        if string_status is None:
            return None
        if string_status.upper() == "ACTIVE":
            return Status.Active
        if string_status.upper() == "INACTIVE":
            return Status.Inactive
        if string_status.upper() == "PENDING":
            return Status.Pending
        return None

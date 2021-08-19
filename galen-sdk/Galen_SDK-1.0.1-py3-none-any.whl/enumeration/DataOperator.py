"""
DataOperator Enum Class
"""

from enum import Enum


class DataOperator(Enum):
    Equal = 1
    GreaterThan = 2
    GreaterThanOrEqual = 3
    LessThan = 4
    LessThanOrEqual = 5
    Like = 6
    Between = 7

    @staticmethod
    def to_string(data_operator) -> str:
        """
        Static Function
        Turns the IntEnum into the a string corresponding to is value - Helper function
        :param data_operator: dataOperator
        :return: a string corresponding to is value
        """
        if data_operator == DataOperator.Equal:
            return "Equal"
        if data_operator == DataOperator.GreaterThan:
            return "GreaterThan"
        if data_operator == DataOperator.GreaterThanOrEqual:
            return "GreaterThanOrEqual"
        if data_operator == DataOperator.LessThan:
            return "LessThan"
        if data_operator == DataOperator.LessThanOrEqual:
            return "LessThanOrEqual"
        if data_operator == DataOperator.Like:
            return "Like"
        if data_operator == DataOperator.Between:
            return "Between"
        return ""

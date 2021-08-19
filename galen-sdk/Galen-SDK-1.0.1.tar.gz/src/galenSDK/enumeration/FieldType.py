"""
FieldType Enum Class
"""

from enum import IntEnum


class FieldType (IntEnum):
    SingleLineText = 1
    MultiLineText = 2
    SingleSelect = 3
    MultiSelect = 4
    Date = 5
    DateTime = 6

    @staticmethod
    def to_string(fieldType) -> str:
        """
        Static Function
        Turns the IntEnum into the a string corresponding to is value - Helper function
        :param fieldType: fieldType
        :return: String corresponding to is intEnum value
        """
        if fieldType == FieldType.SingleLineText:
            return "SingleLineText"
        if fieldType == FieldType.MultiLineText:
            return "MultiLineText"
        if fieldType == FieldType.SingleSelect:
            return "SingleSelect"
        if fieldType == FieldType.MultiSelect:
            return "MultiSelect"
        if fieldType == FieldType.Date:
            return "Date"
        if fieldType == FieldType.DateTime:
            return "DateTime"

    @staticmethod
    def from_string(field_type_string: str):
        """
        Static Function
        Turns the string into the a fieldType enum corresponding to is value - Helper function
        :param field_type_string: string
        :return: fieldType corresponding to the input string
        """
        if field_type_string == "SingleLineText":
            return FieldType.SingleLineText
        if field_type_string == "MultiLineText":
            return FieldType.MultiLineText
        if field_type_string == "SingleSelect":
            return FieldType.SingleSelect
        if field_type_string == "MultiSelect":
            return FieldType.MultiSelect
        if field_type_string == "Date":
            return FieldType.Date
        if field_type_string == "DateTime":
            return FieldType.DateTime

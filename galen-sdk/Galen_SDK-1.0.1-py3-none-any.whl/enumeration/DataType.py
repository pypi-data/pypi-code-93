"""
DataType Enum Class
"""

from enum import Enum


class DataType(Enum):
    Text = 1
    Number = 2
    Date = 3
    DateAndTime = 4
    Boolean = 5
    Image = 6
    Video = 7
    Audio = 8
    File = 9
    GeoCoordinates = 10
    Xml = 11
    Json = 12
    NumberArray = 13
    Temperature = 14
    Height = 15
    Weight = 16
    BloodPressure = 17
    Enumeration = 18

    @staticmethod
    def has_value_type(dataType) -> bool:
        """
        Returns if the current data type needs a value type.
        :param dataType: dataType you want to check. Required.
        :return: true if the current data type needs a value type, false otherwise.
        """
        if dataType == DataType.Image:
            return True
        if dataType == DataType.Video:
            return True
        if dataType == DataType.Audio:
            return True
        if dataType == DataType.Temperature:
            return True
        if dataType == DataType.Height:
            return True
        if dataType == DataType.Weight:
            return True
        return False

    @staticmethod
    def is_media_type(dataType) -> bool:
        """
        Returns if the current data type is a media type.
        :param dataType: dataType you want to check. Required.
        :return: true if the current data type is a media type, false otherwise.
        """

        if dataType == DataType.Image:
            return True
        if dataType == DataType.Video:
            return True
        if dataType == DataType.Audio:
            return True
        if dataType == DataType.File:
            return True
        return False

    @staticmethod
    def can_have_validation(dataType) -> bool:
        """
        Returns if the current data type can have validation rules.
        :param dataType: dataType you want to check. Required.
        :return: true if the current data type can have validation rules.
        """
        if dataType == DataType.Text:
            return True
        if dataType == DataType.Number:
            return True
        if dataType == DataType.Date:
            return True
        if dataType == DataType.DateAndTime:
            return True
        if dataType == DataType.Temperature:
            return True
        if dataType == DataType.Height:
            return True
        if dataType == DataType.Weight:
            return True
        if dataType == DataType.Enumeration:
            return True
        if dataType == DataType.File:
            return True
        return False

    @staticmethod
    def has_predefined_values(dataType) -> bool:
        """
        Returns whether a data type has predefined set of values or not.
        :param dataType: dataType you want to check. Required.        
        :return: true if data type has predefined set of values, else returns false.
        """
        if dataType == DataType.Enumeration:
            return True
        return False

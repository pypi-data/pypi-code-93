"""
FieldArea Enum Class
"""
from enum import IntEnum


class FieldArea (IntEnum):
    UserProfile = 1
    PracticeProfile = 2
    SupplierProfile = 3
    TenantProfile = 4

    @staticmethod
    def to_string(fieldArea) -> str:
        """
        Static Function
        Turns the IntEnum into the a string corresponding to is value - Helper function
        :param fieldArea: fieldArea
        :return: a string corresponding to is value
        """
        if fieldArea == FieldArea.UserProfile:
            return "UserProfile"
        if fieldArea == FieldArea.PracticeProfile:
            return "PracticeProfile"
        if fieldArea == FieldArea.SupplierProfile:
            return "SupplierProfile"
        if fieldArea == FieldArea.TenantProfile:
            return "TenantProfile"

    @staticmethod
    def from_string(field_area_string: str):
        """
        Static Function
        Turns the string into the a FieldArea enum corresponding to is value - Helper function
        :param field_area_string: string
        :return: a fieldArea corresponding to is value
        """
        if field_area_string == "UserProfile":
            return FieldArea.UserProfile
        if field_area_string == "PracticeProfile":
            return FieldArea.PracticeProfile
        if field_area_string == "SupplierProfile":
            return FieldArea.SupplierProfile
        if field_area_string == "TenantProfile":
            return FieldArea.TenantProfile

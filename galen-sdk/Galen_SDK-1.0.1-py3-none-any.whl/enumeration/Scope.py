"""
Scope Enum Class
"""

from enum import Enum


class Scope(Enum):
    PATIENT = 1
    PRACTICE = 2
    SUPPLIER = 3
    TENANT = 4

    @staticmethod
    def to_string(scope) -> str:
        """
        Helper function that parses a scope enum to a string
        :param scope: Scope Enum that will be converted to a string
        """
        if scope is None:
            return scope
        if scope == Scope.PATIENT:
            return "Patient"
        if scope == Scope.PRACTICE:
            return "Practice"
        if scope == Scope.SUPPLIER:
            return "Supplier"
        if scope == Scope.TENANT:
            return "Tenant"
        return None

    @staticmethod
    def string_to_scope(string_scope: str):
        """
        Helper function that parses string into a scope enum
        :param string_scope: string that will be converted to Gender Enum
        """
        if string_scope is None:
            return string_scope
        if string_scope.upper() == "PATIENT":
            return Scope.PATIENT
        if string_scope.upper() == "PRACTICE":
            return Scope.PRACTICE
        if string_scope.upper() == "SUPPLIER":
            return Scope.SUPPLIER
        if string_scope.upper() == "TENANT":
            return Scope.TENANT
        return None

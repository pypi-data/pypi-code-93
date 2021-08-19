"""
Role Enum Class
"""

from enum import IntEnum


class Role (IntEnum):
    SystemAdmin = 1
    CustomerServiceRep = 2
    TenantAdmin = 3
    TenantUser = 4
    SupplierAdmin = 5
    SupplierUser = 6
    PracticeAdmin = 7
    PracticeUser = 8
    Patient = 9
    Guest = 10

    @staticmethod
    def get_roles_for_access_preference():
        """
        Gets all the roles that can be configured access management in tenant preferences.
        :return: the list of roles
        """
        roles = []
        roles.add(Role.TenantUser.__str__())
        roles.add(Role.SupplierAdmin.__str__())
        roles.add(Role.SupplierUser.__str__())
        roles.add(Role.PracticeAdmin.__str__())
        roles.add(Role.PracticeUser.__str__())
        roles.add(Role.Patient.__str__())
        roles.add(Role.Guest.__str__)
        return roles

    @staticmethod
    def to_string(role) -> str:
        """
        Helper method that turns a role into a string
        """
        if role == 1:
            return "SystemAdmin"
        if role == 2:
            return "CustomerServiceRep"
        if role == 3:
            return "TenantAdmin"
        if role == 4:
            return "TenantUser"
        if role == 5:
            return "SupplierAdmin"
        if role == 6:
            return "SupplierUser"
        if role == 7:
            return "PracticeAdmin"
        if role == 8:
            return "PracticeUser"
        if role == 9:
            return "Patient"
        if role == 10:
            return "Guest"

    @staticmethod
    def str_to_enum(role: str):
        if role == "SystemAdmin":
            return Role.SystemAdmin
        if role == "CustomerServiceRep":
            return Role.CustomerServiceRep
        if role == "TenantAdmin":
            return Role.TenantAdmin
        if role == "TenantUser":
            return Role.TenantAdmin
        if role == "SupplierAdmin":
            return Role.SupplierAdmin
        if role == "SupplierUser":
            return Role.SupplierUser
        if role == "PracticeAdmin":
            return Role.PracticeAdmin
        if role == "PracticeUser":
            return Role.PracticeUser
        if role == "Patient":
            return Role.Patient
        if role == "Guest":
            return Role.Guest

    @staticmethod
    def is_greater_than_or_equal(roleOne, roleTwo):
        """
        Returns whether the roleOne is greater or equal in access from the roleTwo.
        :param roleOne: The role against which roleTwo is compared.
        :param roleTwo: The role against which roleOne is compared.
        :return: true if current roleOne is greater than or equal to roleTwo, else false.
        """
        if roleOne == Role.SystemAdmin or roleOne == Role.CustomerServiceRep:
            return roleTwo == Role.SystemAdmin or \
                   roleTwo == Role.CustomerServiceRep
        if roleOne == Role.TenantAdmin:
            return roleTwo == Role.SystemAdmin or \
                   roleTwo == Role.CustomerServiceRep or \
                   Role.TenantAdmin
        if roleOne == Role.TenantUser:
            return roleTwo == Role.SystemAdmin or \
                   roleTwo == Role.CustomerServiceRep or \
                   roleTwo == Role.TenantAdmin or \
                   roleTwo == Role.TenantUser
        if roleOne == Role.SupplierAdmin:
            return roleTwo == Role.SystemAdmin or \
                   roleTwo == Role.CustomerServiceRep or \
                   roleTwo == Role.TenantAdmin or \
                   roleTwo == Role.TenantUser or \
                   roleTwo == Role.SystemAdmin
        if roleOne == Role.SupplierUser:
            return roleTwo == Role.SystemAdmin or \
                   roleTwo == Role.CustomerServiceRep or \
                   roleTwo == Role.TenantAdmin or \
                   roleTwo == Role.TenantUser or \
                   roleTwo == Role.SystemAdmin or \
                   roleTwo == Role.SupplierUser
        if roleOne == Role.SupplierUser:
            return roleTwo == Role.SystemAdmin or \
                   roleTwo == Role.CustomerServiceRep or \
                   roleTwo == Role.TenantAdmin or \
                   roleTwo == Role.TenantUser or \
                   roleTwo == Role.SystemAdmin or \
                   roleTwo == Role.SupplierUser
        if roleOne == Role.PracticeAdmin:
            return roleTwo == Role.SystemAdmin or \
                   roleTwo == Role.CustomerServiceRep or \
                   roleTwo == Role.TenantAdmin or \
                   roleTwo == Role.TenantUser or \
                   roleTwo == Role.SystemAdmin or \
                   roleTwo == Role.SupplierUser or \
                   roleTwo == Role.PracticeAdmin
        if roleOne == Role.PracticeUser:
            return roleTwo == Role.SystemAdmin or \
                   roleTwo == Role.CustomerServiceRep or \
                   roleTwo == Role.TenantAdmin or \
                   roleTwo == Role.TenantUser or \
                   roleTwo == Role.SystemAdmin or \
                   roleTwo == Role.SupplierUser or \
                   roleTwo == Role.PracticeAdmin or \
                   roleTwo == Role.PracticeUser
        if roleOne == Role.Patient:
            return roleTwo != Role.Guest
        return True

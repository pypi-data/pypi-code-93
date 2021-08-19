"""
UserRole Class
"""

from galenSDK.enumeration.Role import Role
from galenSDK.model.Practice import Practice
from galenSDK.model.Supplier import Supplier


class UserRole:
    # private Role role;
    role = None
    # private Supplier supplier;
    supplier = None
    # private Practice practice;
    practice = None
    # private boolean defaultRole = true;
    defaultRole = True

    def __init__(self, role=None, supplier=None, practice=None, defaultRole=True):
        """
        Initializer for the UserRole Class
        :param role: role to set. Optional.
        :param supplier: supplier to set. Optional.
        :param practice: practice to set. Optional.
        :param defaultRole: defaultRole to set. Optional.
        """
        self.role = role
        self.supplier = supplier
        self.practice = practice
        self.defaultRole = defaultRole

    @staticmethod
    def from_json(json_dict):
        json_dict_holder = {}
        if "role" in json_dict:
            json_dict_holder["role"] = Role.str_to_enum(json_dict["role"])
        if "supplier" in json_dict:
            json_dict_holder["supplier"] = json_dict["supplier"]
        if "practice" in json_dict:
            json_dict_holder["practice"] = json_dict["practice"]
        if "defaultRole" in json_dict:
            json_dict_holder["defaultRole"] = json_dict["defaultRole"]
        return UserRole(**json_dict_holder)

    def get_role(self) -> Role:
        """
        :return: role
        """
        return self.role

    def set_role(self, role: Role):
        """
        :param role: the role to set
        """
        self.role = role

    def get_supplier(self) -> Supplier:
        """
        :return: supplier
        """
        return self.supplier

    def set_supplier(self, supplier: Supplier):
        """
        :param supplier: the supplier to set
        """
        self.supplier = supplier

    def get_practice(self) -> Practice:
        """
        :return: practice
        """
        return self.practice

    def set_practice(self, practice: Practice):
        """
        :param practice: the practice to set
        """
        self.practice = practice

    def is_default_role(self) -> bool:
        """
        :return: defaultRole
        """
        return self.defaultRole

    def set_default_role(self, defaultRole: bool):
        """
        :param defaultRole: the defaultRole to set
        """
        self.defaultRole = defaultRole

    def __hash__(self):
        """
        __hash__ overloaded function
        Hash Function for the UserRole Class
        :returns: An int representing the hash value of the object
        """
        prime = 31
        result = 1
        result = prime * result + (1231 if self.defaultRole else 1237)
        result = prime * result + (self.practice.__hash__() if self.practice else 0)
        result = prime * result + (self.role.__hash__() if self.role else 0)
        result = prime * result + (self.supplier.__hash__() if self.supplier else 0)
        return result

    def __eq__(self, other):
        """
        __eq__ overloaded function
        :param other: the object to compare this UserRole to
        :returns: True if both objects are equivalent, otherwise false
        """
        if not isinstance(other, UserRole):
            return False
        if self.defaultRole != other.defaultRole:
            return False
        if self.practice is None:
            if other.practice is not None:
                return False
        elif self.practice != other.practice:
            return False
        if self.role != other.role:
            return False
        if self.supplier is None:
            if other.supplier is not None:
                return False
        elif self.supplier != other.supplier:
            return False
        return True

    def __str__(self):
        """
        __str__ overloaded function
        Turns the UserRole object into a string
        :return: string representing the UserRole object
        """
        holder = ""
        holder += "UserRole [role=" + (self.role.__str__() if self.role else "") + \
                  ", supplier=" + (self.supplier.__str__() if self.supplier else "") + \
                  ", practice=" + (self.practice.__str__() if self.practice else "") + \
                  ", defaultRole=" + ("True" if self.defaultRole else "False") + "]"
        return holder

    def __dict__(self):
        """
        __dict__ overloaded function
        :return: a dictionary of the UserRole variables.
        """
        x = {
            "role": Role.to_string(self.role),
            "supplier": self.supplier,
            "practice": self.practice,
            "defaultRole": self.defaultRole
        }
        return x

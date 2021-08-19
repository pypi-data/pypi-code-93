"""
OwnerFilter Class
"""


class OwnerFilter:
    tenantId = None
    users = []
    practices = []
    suppliers = []

    def __init__(self, tenantId: str = None, users: [str] = [], suppliers: [str] = [], practices: [str] = []):
        """
        Initializer for the OwnerFilter Class
        :param tenantId: tenantId string. Optional.
        :param users: list of Users. Optional.
        :param suppliers: list of Suppliers. Optional.
        :param practices: list of Practices. Optional.
        """
        self.tenantId = tenantId
        self.users = users
        self.suppliers = suppliers
        self.practices = practices

    def set_tenant(self, tenantId: str):
        """
        :param tenantId: tenantId to set
        """
        self.tenantId = tenantId

    def get_tenant_id(self) -> str:
        """
        :return: returns the TenantId
        """
        return self.tenantId

    def set_users(self, users: [str]):
        """
        :param users: list of Users to set
        """
        self.users = users

    def add_user(self, user: str):
        """
        :param user: a single User to add to the list
        """
        self.users.append(user)

    def get_users(self) -> [str]:
        """
        :return: list of users
        """
        return self.users

    def set_suppliers(self, suppliers: [str]):
        """
        :param suppliers: list of Suppliers to set
        """
        self.suppliers = suppliers

    def add_supplier(self, supplier: str):
        """
        :param supplier: a single Supplier to add to the list
        """
        self.suppliers.append(supplier)

    def get_suppliers(self) -> [str]:
        """
        :return: list of suppliers
        """
        return self.suppliers

    def set_practices(self, practices: [str]):
        """
        :param practices: list of Practices to set
        """
        self.practices = practices

    def add_practice(self, practice: str):
        """
        :param practice: a single Practice to add to the list
        """
        self.practices.append(practice)

    def get_practices(self) -> [str]:
        """
        :return: list of practices
        """
        return self.practices

    def __hash__(self):
        """
        __hash__ overloaded function
        Hash Function for the OwnerFilter Class
        :returns: An int representing the hash value of the object
        """
        prime = 31
        result = 1
        result = prime * result + (0 if self.users == [] else self.users.__hash__)
        result = prime * result + (0 if self.suppliers == [] else self.suppliers.__hash__)
        result = prime * result + (0 if self.practices == [] else self.practices.__hash__)
        result = prime * result + (0 if self.tenantId is None else self.tenantId.__hash__)
        return result

    def __eq__(self, other):
        """
        __eq__ overloaded function
        :param other: the object to compare this DeviceCriteria to
        :returns: True if both objects are equivalent, otherwise false
        """
        if not isinstance(other, OwnerFilter):
            return False
        if self.users != other.users:
            return False
        if self.suppliers != other.suppliers:
            return False
        if self.practices != other.practices:
            return False
        if self.tenantId != other.tenantId:
            return False
        return True

    def __str__(self):
        """
        __str__ overloaded function
        Turns the OwnerFilter object into a string
        :return: string representing the OwnerFilter object
        """
        holder = ""
        holder += "UserFilter [users=" + (self.users.__str__() if self.users else "") + \
                  ", practices=" + (self.practices.__str__() if self.practices else "") + \
                  ", suppliers=" + (self.suppliers.__str__() if self.suppliers else "") + \
                  ", tenantId=" + (self.tenantId.__str__() if self.tenantId else "") + "]"
        return holder

    def __dict__(self):
        """
        __dict__ overloaded function
        :return: a dictionary of the OwnerFilter variables.
        """
        x = {
            "tenantId": self.tenantId,
            "users": self.users,
            "practices": self.practices,
            "suppliers": self.suppliers
        }
        return x

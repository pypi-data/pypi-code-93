"""
ContactInfo Class
"""


class ContactInfo:
    # private String streetAddress1;
    streetAddress1 = None
    # private String streetAddress2;
    streetAddress2 = None
    # private String city;
    city = None
    # private String state;
    state = None
    # private String country;
    country = None
    # private String zipcode;
    zipcode = None
    # private String primaryPhone;
    primaryPhone = None
    # private String secondaryPhone;
    secondaryPhone = None
    # private Boolean primaryPhoneVerified;
    primaryPhoneVerified = None

    def __init__(self, streetAddress1: str = None, streetAddress2: str = None, city: str = None, state: str = None,
                 country: str = None, zipcode: str = None, primaryPhone: str = None, secondaryPhone: str = None,
                 primaryPhoneVerified: bool = None):
        """
        The initializer for the ContactInfo Class
        :param streetAddress1: streetAddress1 to set. Optional.
        :param streetAddress2: streetAddress2 to set. Optional.
        :param city: city to set. Optional.
        :param state: state to set. Optional.
        :param country: country to set. Optional.
        :param zipcode: zipcode to set. Optional.
        :param primaryPhone: primaryPhone to set. Optional.
        :param secondaryPhone: secondaryPhone to set. Optional.
        :param primaryPhoneVerified: primaryPhoneVerified to set. Optional.
        """

        self.streetAddress1 = streetAddress1.__str__()
        self.streetAddress2 = streetAddress2.__str__()
        self.city = city.__str__()
        self.state = state.__str__()
        self.country = country.__str__()
        self.zipcode = zipcode.__str__()
        self.primaryPhone = primaryPhone.__str__()
        self.secondaryPhone = secondaryPhone.__str__()
        self.primaryPhoneVerified = primaryPhoneVerified

    @staticmethod
    def from_json(json_dict):
        """
        Takes in a dictionary and returns an ContactInfo object [Helper function for SDK]
        :param json_dict: dictionary to turn into User ContactInfo
        :return: ContactInfo
        """
        json_dict_holder = {}
        if "streetAddress1" in json_dict:
            json_dict_holder["streetAddress1"] = json_dict["streetAddress1"]
        if "streetAddress2" in json_dict:
            json_dict_holder["streetAddress2"] = json_dict["streetAddress2"]
        if "city" in json_dict:
            json_dict_holder["city"] = json_dict["city"]
        if "state" in json_dict:
            json_dict_holder["state"] = json_dict["state"]
        if "country" in json_dict:
            json_dict_holder["country"] = json_dict["country"]
        if "zipcode" in json_dict:
            json_dict_holder["zipcode"] = json_dict["zipcode"]
        if "primaryPhone" in json_dict:
            json_dict_holder["primaryPhone"] = json_dict["primaryPhone"]
        if "secondaryPhone" in json_dict:
            json_dict_holder["secondaryPhone"] = json_dict["secondaryPhone"]
        if "primaryPhoneVerified" in json_dict:
            json_dict_holder["primaryPhoneVerified"] = json_dict["primaryPhoneVerified"]
        return ContactInfo(**json_dict_holder)

    def get_street_address1(self) -> str:
        """
        :return: streetAddress1
        """
        return self.streetAddress1

    def set_street_address1(self, streetAddress1: str):
        """
        :param streetAddress1: The streetAddress1 to set
        """
        self.streetAddress1 = streetAddress1.__str__()

    def get_street_address2(self) -> str:
        """
        :return: streetAddress2
        """
        return self.streetAddress2

    def set_street_address2(self, streetAddress2: str):
        """
        :param streetAddress2: the streetAddress2 to set
        """
        self.streetAddress2 = streetAddress2.__str__()

    def get_city(self) -> str:
        """
        :return: city
        """
        return self.city

    def set_city(self, city: str):
        """
        :param city: the city to set
        """
        self.city = city.__str__()

    def get_state(self) -> str:
        """
        :return: state
        """
        return self.state

    def set_state(self, state: str):
        """
        :param state: the state to set
        """
        self.state = state.__str__()

    def get_country(self) -> str:
        """
        :return: country
        """
        return self.country

    def set_country(self, country: str):
        """
        :param country: the country to set
        """
        self.country = country.__str__()

    def get_zipcode(self) -> str:
        """
        :return: zipcode
        """
        return self.zipcode

    def set_zipcode(self, zipcode: str):
        """
        :param zipcode: the zipcode to set
        """
        self.zipcode = zipcode.__str__()

    def get_primary_phone(self) -> str:
        """
        :return: primaryPhone
        """
        return self.primaryPhone

    def set_primary_phone(self, primaryPhone: str):
        """
        :param primaryPhone: the primaryPhone to set
        """
        self.primaryPhone = primaryPhone.__str__()

    def get_secondary_phone(self) -> str:
        """
        :return: secondaryPhone
        """
        return self.secondaryPhone

    def set_secondary_phone(self, secondaryPhone: str):
        """
        :param secondaryPhone: the secondaryPhone to set
        """
        self.secondaryPhone = secondaryPhone.__str__()

    def get_primary_phone_verified(self) -> bool:
        """
        :return: primaryPhoneVerified
        """
        return self.primaryPhoneVerified

    def set_primary_phone_verified(self, primaryPhoneVerified: bool):
        """
        :param primaryPhoneVerified: the primaryPhoneVerified to set
        """
        self.primaryPhone = primaryPhoneVerified

    def __hash__(self):
        """
        __hash__ overloaded function
        Hash Function for the ContactInfo Class
        :returns: An int representing the hash value of the object
        """
        prime = 31
        result = 1
        result = prime * result + (0 if self.city is None else self.city.__hash__())
        result = prime * result + (0 if self.country is None else self.country.__hash__())
        result = prime * result + (0 if self.primaryPhone is None else self.primaryPhone.__hash__())
        result = prime * result + (0 if self.secondaryPhone is None else self.secondaryPhone.__hash__())
        result = prime * result + (0 if self.state is None else self.state.__hash__())
        result = prime * result + (0 if self.streetAddress1 is None else self.streetAddress1.__hash__())
        result = prime * result + (0 if self.streetAddress2 is None else self.streetAddress2.__hash__())
        result = prime * result + (0 if self.zipcode is None else self.zipcode.__hash__())
        return result

    def __eq__(self, other):
        """
        __eq__ overloaded function
        :param other: the object to compare this ContactInfo to
        :returns: True if both objects are equivalent, otherwise false
        """
        if not isinstance(other, ContactInfo):
            return False
        if self.city is None:
            if other.city is not None:
                return False
        elif self.city != other.city:
            return False
        if self.country is None:
            if other.country is not None:
                return False
        elif self.country != other.country:
            return False
        if self.primaryPhone is None:
            if other.primaryPhone is not None:
                return False
        elif self.primaryPhone != other.primaryPhone:
            return False
        if self.secondaryPhone is None:
            if other.secondaryPhone is not None:
                return False
        elif self.secondaryPhone != other.secondaryPhone:
            return False
        if self.state is None:
            if other.state is not None:
                return False
        elif self.state != other.state:
            return False
        if self.streetAddress1 is None:
            if other.streetAddress1 is not None:
                return False
        elif self.streetAddress1 != other.streetAddress1:
            return False
        if self.streetAddress2 is None:
            if other.streetAddress2 is not None:
                return False
        elif self.streetAddress2 != other.streetAddress2:
            return False
        if self.zipcode is None:
            if other.zipcode is not None:
                return False
        elif self.zipcode != other.zipcode:
            return False
        return True

    def __str__(self):
        """
        __str__ overloaded function
        Turns the ContactInfo object into a string
        :return: string representing the ContactInfo object
        """
        holder = ""
        holder += "ContactInfo [streetAddress1=" + self.streetAddress1 + ", streetAddress2=" + self.streetAddress2 + \
                  ", city=" + self.city + ", state=" + self.state + ", country=" + self.country + ", zipcode=" + \
                  self.zipcode + ", primaryPhone=" + self.primaryPhone + ", secondaryPhone=" + self.secondaryPhone + "]"
        return holder

    def __dict__(self):
        """
        __dict__ overloaded function
        :return: a dictionary of the ContactInfo variables.
        """
        x = {
            "streetAddress1": self.streetAddress1,
            "streetAddress2": self.streetAddress2,
            "city": self.city,
            "state": self.state,
            "country": self.country,
            "zipcode": self.zipcode,
            "primaryPhone": self.primaryPhone,
            "secondaryPhone": self.secondaryPhone
        }
        return x

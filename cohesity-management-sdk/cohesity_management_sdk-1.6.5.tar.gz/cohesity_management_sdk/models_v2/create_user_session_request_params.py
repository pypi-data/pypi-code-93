# -*- coding: utf-8 -*-


class CreateUserSessionRequestParams(object):

    """Implementation of the 'CreateUserSessionRequestParams' model.

    Specifies user session request parameters

    Attributes:
        username (string): Specifies the login name of the Cohesity user
        password (string): Specifies the password of the Cohesity user
        domain (string): Specifies the domain the user is logging in to. For a
            local user the domain is LOCAL. For LDAP/AD user, the domain will
            map to a LDAP connection string. A user is uniquely identified by
            a combination of username and domain. LOCAL is the default
            domain.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "username":'username',
        "password":'password',
        "domain":'domain'
    }

    def __init__(self,
                 username=None,
                 password=None,
                 domain=None):
        """Constructor for the CreateUserSessionRequestParams class"""

        # Initialize members of the class
        self.username = username
        self.password = password
        self.domain = domain


    @classmethod
    def from_dictionary(cls,
                        dictionary):
        """Creates an instance of this model from a dictionary

        Args:
            dictionary (dictionary): A dictionary representation of the object as
            obtained from the deserialization of the server's response. The keys
            MUST match property names in the API description.

        Returns:
            object: An instance of this structure class.

        """
        if dictionary is None:
            return None

        # Extract variables from the dictionary
        username = dictionary.get('username')
        password = dictionary.get('password')
        domain = dictionary.get('domain')

        # Return an object of this model
        return cls(username,
                   password,
                   domain)



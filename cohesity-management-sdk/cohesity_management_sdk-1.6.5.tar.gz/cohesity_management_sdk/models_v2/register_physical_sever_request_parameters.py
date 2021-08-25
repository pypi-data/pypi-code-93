# -*- coding: utf-8 -*-


class RegisterPhysicalSeverRequestParameters(object):

    """Implementation of the 'Register physical sever request parameters.' model.

    Specifies parameters to register physical server.

    Attributes:
        endpoint (string): Specifies the endpoint IPaddress, URL or hostname
            of the physical host.
        force_register (bool): The agent running on a physical host will fail
            the registration if it is already registered as part of another
            cluster. By setting this option to true, agent can be forced to
            register with the current cluster.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "endpoint":'endpoint',
        "force_register":'forceRegister'
    }

    def __init__(self,
                 endpoint=None,
                 force_register=None):
        """Constructor for the RegisterPhysicalSeverRequestParameters class"""

        # Initialize members of the class
        self.endpoint = endpoint
        self.force_register = force_register


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
        endpoint = dictionary.get('endpoint')
        force_register = dictionary.get('forceRegister')

        # Return an object of this model
        return cls(endpoint,
                   force_register)



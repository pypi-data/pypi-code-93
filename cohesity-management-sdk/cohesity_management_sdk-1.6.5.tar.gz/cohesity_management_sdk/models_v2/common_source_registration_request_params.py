# -*- coding: utf-8 -*-


class CommonSourceRegistrationRequestParams(object):

    """Implementation of the 'CommonSourceRegistrationRequestParams' model.

    Specifies the parameters which are common between all Protection Source
    registrations.

    Attributes:
        environment (Environment8Enum): Specifies the environment type of the
            Protection Source.
        name (string): A user specified name for this source.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "environment":'environment',
        "name": 'name'
    }

    def __init__(self,
                 environment=None,
                 name=None):
        """Constructor for the CommonSourceRegistrationRequestParams class"""

        # Initialize members of the class
        self.environment = environment
        self.name = name


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
        environment = dictionary.get('environment')
        name = dictionary.get('name')

        # Return an object of this model
        return cls(environment, name)



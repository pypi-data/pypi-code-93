# -*- coding: utf-8 -*-


class UdaProtectionGroupObjectParams(object):

    """Implementation of the 'UdaProtectionGroupObjectParams' model.

    Specifies the Universal Data Adapter object details.

    Attributes:
        name (string): Specifies the fully qualified name of the object.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "name":'name'
    }

    def __init__(self,
                 name=None):
        """Constructor for the UdaProtectionGroupObjectParams class"""

        # Initialize members of the class
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
        name = dictionary.get('name')

        # Return an object of this model
        return cls(name)



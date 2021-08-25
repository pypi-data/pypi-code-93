# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.protection_group

class ProtectionGroups(object):

    """Implementation of the 'ProtectionGroups' model.

    Protection Group  response.

    Attributes:
        protection_groups (list of ProtectionGroup): Specifies the list of
            Protection Groups which were returned by the request.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "protection_groups":'protectionGroups'
    }

    def __init__(self,
                 protection_groups=None):
        """Constructor for the ProtectionGroups class"""

        # Initialize members of the class
        self.protection_groups = protection_groups


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
        protection_groups = None
        if dictionary.get('protectionGroups') != None:
            protection_groups = list()
            for structure in dictionary.get('protectionGroups'):
                protection_groups.append(cohesity_management_sdk.models_v2.protection_group.ProtectionGroup.from_dictionary(structure))

        # Return an object of this model
        return cls(protection_groups)



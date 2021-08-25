# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.container_database_info

class DatabaseEntityInfo(object):

    """Implementation of the 'DatabaseEntityInfo' model.

    Object details about Oracle database entity info.

    Attributes:
        container_database_info (ContainerDatabaseInfo): Object details about
            Oracle container database.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "container_database_info":'containerDatabaseInfo'
    }

    def __init__(self,
                 container_database_info=None):
        """Constructor for the DatabaseEntityInfo class"""

        # Initialize members of the class
        self.container_database_info = container_database_info


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
        container_database_info = cohesity_management_sdk.models_v2.container_database_info.ContainerDatabaseInfo.from_dictionary(dictionary.get('containerDatabaseInfo')) if dictionary.get('containerDatabaseInfo') else None

        # Return an object of this model
        return cls(container_database_info)



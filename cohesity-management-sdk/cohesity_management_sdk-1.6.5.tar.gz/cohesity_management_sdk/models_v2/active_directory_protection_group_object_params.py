# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.active_directory_app_parameters

class ActiveDirectoryProtectionGroupObjectParams(object):

    """Implementation of the 'Active Directory Protection Group Object Params.' model.

    Specifies the object identifier to for the active directory protection
    group.

    Attributes:
        source_id (long|int): Specifies the id of the registered active
            directory source.
        source_name (string): Specifies the name of the registered active
            directory source.
        app_params (list of ActiveDirectoryAppParameters): Specifies the
            specific parameters required for active directory app
            configuration.
        enable_system_backup (bool): Specifies whether to take bmr backup. If
            this is not specified, the bmr backup won't be enabled.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "source_id":'sourceId',
        "source_name":'sourceName',
        "app_params":'appParams',
        "enable_system_backup":'enableSystemBackup'
    }

    def __init__(self,
                 source_id=None,
                 source_name=None,
                 app_params=None,
                 enable_system_backup=None):
        """Constructor for the ActiveDirectoryProtectionGroupObjectParams class"""

        # Initialize members of the class
        self.source_id = source_id
        self.source_name = source_name
        self.app_params = app_params
        self.enable_system_backup = enable_system_backup


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
        source_id = dictionary.get('sourceId')
        source_name = dictionary.get('sourceName')
        app_params = None
        if dictionary.get('appParams') != None:
            app_params = list()
            for structure in dictionary.get('appParams'):
                app_params.append(cohesity_management_sdk.models_v2.active_directory_app_parameters.ActiveDirectoryAppParameters.from_dictionary(structure))
        enable_system_backup = dictionary.get('enableSystemBackup')

        # Return an object of this model
        return cls(source_id,
                   source_name,
                   app_params,
                   enable_system_backup)



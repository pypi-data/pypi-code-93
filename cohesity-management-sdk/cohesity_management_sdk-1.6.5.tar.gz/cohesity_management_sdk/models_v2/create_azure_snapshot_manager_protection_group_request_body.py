# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.azure_snapshot_manager_protection_group_object_params

class CreateAzureSnapshotManagerProtectionGroupRequestBody(object):

    """Implementation of the 'Create Azure Snapshot Manager Protection Group Request Body' model.

    Specifies the parameters which are specific to Azure related Protection
    Groups using Azure native snapshot orchestration with snapshot manager.
    Objects must be specified.

    Attributes:
        objects (list of AzureSnapshotManagerProtectionGroupObjectParams):
            Specifies the objects to be included in the Protection Group.
        exclude_object_ids (list of long|int): Specifies the objects to be
            excluded in the Protection Group.
        source_id (long|int): Specifies the id of the parent of the objects.
        source_name (string): Specifies the name of the parent of the
            objects.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "objects":'objects',
        "exclude_object_ids":'excludeObjectIds',
        "source_id":'sourceId',
        "source_name":'sourceName'
    }

    def __init__(self,
                 objects=None,
                 exclude_object_ids=None,
                 source_id=None,
                 source_name=None):
        """Constructor for the CreateAzureSnapshotManagerProtectionGroupRequestBody class"""

        # Initialize members of the class
        self.objects = objects
        self.exclude_object_ids = exclude_object_ids
        self.source_id = source_id
        self.source_name = source_name


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
        objects = None
        if dictionary.get('objects') != None:
            objects = list()
            for structure in dictionary.get('objects'):
                objects.append(cohesity_management_sdk.models_v2.azure_snapshot_manager_protection_group_object_params.AzureSnapshotManagerProtectionGroupObjectParams.from_dictionary(structure))
        exclude_object_ids = dictionary.get('excludeObjectIds')
        source_id = dictionary.get('sourceId')
        source_name = dictionary.get('sourceName')

        # Return an object of this model
        return cls(objects,
                   exclude_object_ids,
                   source_id,
                   source_name)



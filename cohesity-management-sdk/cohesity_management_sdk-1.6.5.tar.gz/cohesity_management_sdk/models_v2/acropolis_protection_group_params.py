# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.acropolis_protection_group_object_params
import cohesity_management_sdk.models_v2.indexing_policy

class AcropolisProtectionGroupParams(object):

    """Implementation of the 'AcropolisProtectionGroupParams' model.

    Specifies the parameters which are related to Acropolis Protection
    Groups.

    Attributes:
        objects (list of AcropolisProtectionGroupObjectParams): Specifies the
            objects included in the Protection Group.
        source_id (long|int): Specifies the id of the parent of the objects.
        source_name (string): Specifies the name of the parent of the
            objects.
        exclude_object_ids (list of long|int): Specifies the object ids to be
            excluded in the Protection Group.
        indexing_policy (IndexingPolicy): Specifies settings for indexing
            files found in an Object (such as a VM) so these files can be
            searched and recovered. This also specifies inclusion and
            exclusion rules that determine the directories to index.
        app_consistent_snapshot (bool): Specifies whether or not to quiesce
            apps and the file system in order to take app consistent
            snapshots. If not specified or false then snapshots will not be
            app consistent.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "objects":'objects',
        "source_id":'sourceId',
        "source_name":'sourceName',
        "exclude_object_ids":'excludeObjectIds',
        "indexing_policy":'indexingPolicy',
        "app_consistent_snapshot":'appConsistentSnapshot'
    }

    def __init__(self,
                 objects=None,
                 source_id=None,
                 source_name=None,
                 exclude_object_ids=None,
                 indexing_policy=None,
                 app_consistent_snapshot=None):
        """Constructor for the AcropolisProtectionGroupParams class"""

        # Initialize members of the class
        self.objects = objects
        self.source_id = source_id
        self.source_name = source_name
        self.exclude_object_ids = exclude_object_ids
        self.indexing_policy = indexing_policy
        self.app_consistent_snapshot = app_consistent_snapshot


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
                objects.append(cohesity_management_sdk.models_v2.acropolis_protection_group_object_params.AcropolisProtectionGroupObjectParams.from_dictionary(structure))
        source_id = dictionary.get('sourceId')
        source_name = dictionary.get('sourceName')
        exclude_object_ids = dictionary.get('excludeObjectIds')
        indexing_policy = cohesity_management_sdk.models_v2.indexing_policy.IndexingPolicy.from_dictionary(dictionary.get('indexingPolicy')) if dictionary.get('indexingPolicy') else None
        app_consistent_snapshot = dictionary.get('appConsistentSnapshot')

        # Return an object of this model
        return cls(objects,
                   source_id,
                   source_name,
                   exclude_object_ids,
                   indexing_policy,
                   app_consistent_snapshot)



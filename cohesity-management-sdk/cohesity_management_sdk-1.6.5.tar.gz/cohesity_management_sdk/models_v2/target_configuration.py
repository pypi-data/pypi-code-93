# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.replication_target_configuration
import cohesity_management_sdk.models_v2.archival_target_configuration_1

class TargetConfiguration(object):

    """Implementation of the 'Target Configuration' model.

    Specifies the replication and archival targets.

    Attributes:
        replications (list of ReplicationTargetConfiguration): Specifies a
            list of replication targets configurations.
        archivals (list of ArchivalTargetConfiguration1): Specifies a list of
            archival targets configurations.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "replications":'replications',
        "archivals":'archivals'
    }

    def __init__(self,
                 replications=None,
                 archivals=None):
        """Constructor for the TargetConfiguration class"""

        # Initialize members of the class
        self.replications = replications
        self.archivals = archivals


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
        replications = None
        if dictionary.get('replications') != None:
            replications = list()
            for structure in dictionary.get('replications'):
                replications.append(cohesity_management_sdk.models_v2.replication_target_configuration.ReplicationTargetConfiguration.from_dictionary(structure))
        archivals = None
        if dictionary.get('archivals') != None:
            archivals = list()
            for structure in dictionary.get('archivals'):
                archivals.append(cohesity_management_sdk.models_v2.archival_target_configuration_1.ArchivalTargetConfiguration1.from_dictionary(structure))

        # Return an object of this model
        return cls(replications,
                   archivals)



# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.retention

class ArchivalTargetConfiguration1(object):

    """Implementation of the 'Archival Target Configuration1' model.

    Specifies settings for copying Snapshots External Targets (such as AWS or
    Tape). This also specifies the retention policy that should be applied to
    Snapshots after they have been copied to the specified target.

    Attributes:
        id (long|int): Specifies the Archival target to copy the Snapshots
            to.
        archival_target_type (ArchivalTargetTypeEnum): Specifies the
            snapshot's archival target type from which recovery has been
            performed.
        retention (Retention): Specifies the retention of a backup.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "id":'id',
        "archival_target_type":'archivalTargetType',
        "retention":'retention'
    }

    def __init__(self,
                 id=None,
                 archival_target_type=None,
                 retention=None):
        """Constructor for the ArchivalTargetConfiguration1 class"""

        # Initialize members of the class
        self.id = id
        self.archival_target_type = archival_target_type
        self.retention = retention


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
        id = dictionary.get('id')
        archival_target_type = dictionary.get('archivalTargetType')
        retention = cohesity_management_sdk.models_v2.retention.Retention.from_dictionary(dictionary.get('retention')) if dictionary.get('retention') else None

        # Return an object of this model
        return cls(id,
                   archival_target_type,
                   retention)



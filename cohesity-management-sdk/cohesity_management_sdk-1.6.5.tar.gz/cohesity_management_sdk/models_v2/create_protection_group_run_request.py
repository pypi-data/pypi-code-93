# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.run_object
import cohesity_management_sdk.models_v2.target_configuration

class CreateProtectionGroupRunRequest(object):

    """Implementation of the 'CreateProtectionGroupRunRequest' model.

    Specifies the request to create a protection run. On success, the system
    will accept the request and return the Protection Group id for which the
    run is supposed to start. The actual run may start at a later time if the
    system is busy. Consumers must query the Protection Group to see the run.

    Attributes:
        run_type (RunType2Enum): Type of protection run. 'kRegular' indicates
            an incremental (CBT) backup. Incremental backups utilizing CBT (if
            supported) are captured of the target protection objects. The
            first run of a kRegular schedule captures all the blocks. 'kFull'
            indicates a full (no CBT) backup. A complete backup (all blocks)
            of the target protection objects are always captured and Change
            Block Tracking (CBT) is not utilized. 'kLog' indicates a Database
            Log backup. Capture the database transaction logs to allow rolling
            back to a specific point in time. 'kSystem' indicates system
            volume backup. It produces an image for bare metal recovery.
        objects (list of RunObject): Specifies the list of objects to be
            protected by this Protection Group run. These can be leaf objects
            or non-leaf objects in the protection hierarchy. This must be
            specified only if a subset of objects from the Protection Groups
            needs to be protected.
        targets_config (TargetConfiguration): Specifies the replication and
            archival targets.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "run_type":'runType',
        "objects":'objects',
        "targets_config":'targetsConfig'
    }

    def __init__(self,
                 run_type=None,
                 objects=None,
                 targets_config=None):
        """Constructor for the CreateProtectionGroupRunRequest class"""

        # Initialize members of the class
        self.run_type = run_type
        self.objects = objects
        self.targets_config = targets_config


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
        run_type = dictionary.get('runType')
        objects = None
        if dictionary.get('objects') != None:
            objects = list()
            for structure in dictionary.get('objects'):
                objects.append(cohesity_management_sdk.models_v2.run_object.RunObject.from_dictionary(structure))
        targets_config = cohesity_management_sdk.models_v2.target_configuration.TargetConfiguration.from_dictionary(dictionary.get('targetsConfig')) if dictionary.get('targetsConfig') else None

        # Return an object of this model
        return cls(run_type,
                   objects,
                   targets_config)



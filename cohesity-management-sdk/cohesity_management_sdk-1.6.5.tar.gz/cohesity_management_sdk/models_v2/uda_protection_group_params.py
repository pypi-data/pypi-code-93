# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.uda_protection_group_object_params

class UdaProtectionGroupParams(object):

    """Implementation of the 'UdaProtectionGroupParams' model.

    Specifies parameters related to the Universal Data Adapter Protection
    job.

    Attributes:
        source_id (long|int): Specifies the source Id of the objects to be
            protected.
        objects (list of UdaProtectionGroupObjectParams): Specifies a list of
            fully qualified names of the objects to be protected.
        full_backup_args (string): Specifies the custom arguments to be
            supplied to the full backup script when a full backup is enabled
            in the policy.
        incr_backup_args (string): Specifies the custom arguments to be
            supplied to the incremental backup script when an incremental
            backup is enabled in the policy.
        log_backup_args (string): Specifies the custom arguments to be
            supplied to the log backup script when a log backup is enabled in
            the policy.
        concurrency (int): Specifies the maximum number of concurrent IO
            Streams that will be created to exchange data with the cluster. If
            not specified, the default value is taken as 1.
        mounts (int): Specifies the maximum number of view mounts per host. If
            not specified, the default value is taken as 1.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "source_id":'sourceId',
        "objects":'objects',
        "full_backup_args":'fullBackupArgs',
        "incr_backup_args":'incrBackupArgs',
        "log_backup_args":'logBackupArgs',
        "concurrency":'concurrency',
        "mounts":'mounts'
    }

    def __init__(self,
                 source_id=None,
                 objects=None,
                 full_backup_args=None,
                 incr_backup_args=None,
                 log_backup_args=None,
                 concurrency=1,
                 mounts=1):
        """Constructor for the UdaProtectionGroupParams class"""

        # Initialize members of the class
        self.source_id = source_id
        self.objects = objects
        self.full_backup_args = full_backup_args
        self.incr_backup_args = incr_backup_args
        self.log_backup_args = log_backup_args
        self.concurrency = concurrency
        self.mounts = mounts


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
        objects = None
        if dictionary.get('objects') != None:
            objects = list()
            for structure in dictionary.get('objects'):
                objects.append(cohesity_management_sdk.models_v2.uda_protection_group_object_params.UdaProtectionGroupObjectParams.from_dictionary(structure))
        full_backup_args = dictionary.get('fullBackupArgs')
        incr_backup_args = dictionary.get('incrBackupArgs')
        log_backup_args = dictionary.get('logBackupArgs')
        concurrency = dictionary.get("concurrency") if dictionary.get("concurrency") else 1
        mounts = dictionary.get("mounts") if dictionary.get("mounts") else 1

        # Return an object of this model
        return cls(source_id,
                   objects,
                   full_backup_args,
                   incr_backup_args,
                   log_backup_args,
                   concurrency,
                   mounts)



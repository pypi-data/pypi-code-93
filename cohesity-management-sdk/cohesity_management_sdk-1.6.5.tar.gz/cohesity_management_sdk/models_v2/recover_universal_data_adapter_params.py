# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.recover_universal_data_adapter_snapshot_params

class RecoverUniversalDataAdapterParams(object):

    """Implementation of the 'Recover Universal Data Adapter params.' model.

    Specifies the parameters to recover Universal Data Adapter objects.

    Attributes:
        recover_to (long|int): Specifies the 'Source Registration ID' of the
            source where the objects are to be recovered. If this is not
            specified, the recovery job will recover to the original
            location.
        concurrency (int): Specifies the maximum number of concurrent IO
            Streams that will be created to exchange data with the cluster. If
            not specified, the default value is taken as 1.
        mounts (int): Specifies the maximum number of view mounts per host. If
            not specified, the default value is taken as 1.
        recovery_args (string): Specifies the arguments for recovery of
            Universal Data Adapter objects.
        snapshots (list of RecoverUniversalDataAdapterSnapshotParams):
            Specifies the local snapshot ids and other details of the objects
            to be recovered.
        warnings (list of string): This field will hold the warnings in cases
            where the job status is SucceededWithWarnings.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "snapshots":'snapshots',
        "recover_to":'recoverTo',
        "concurrency":'concurrency',
        "mounts":'mounts',
        "recovery_args":'recoveryArgs',
        "warnings":'warnings'
    }

    def __init__(self,
                 snapshots=None,
                 recover_to=None,
                 concurrency=1,
                 mounts=1,
                 recovery_args=None,
                 warnings=None):
        """Constructor for the RecoverUniversalDataAdapterParams class"""

        # Initialize members of the class
        self.recover_to = recover_to
        self.concurrency = concurrency
        self.mounts = mounts
        self.recovery_args = recovery_args
        self.snapshots = snapshots
        self.warnings = warnings


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
        snapshots = None
        if dictionary.get('snapshots') != None:
            snapshots = list()
            for structure in dictionary.get('snapshots'):
                snapshots.append(cohesity_management_sdk.models_v2.recover_universal_data_adapter_snapshot_params.RecoverUniversalDataAdapterSnapshotParams.from_dictionary(structure))
        recover_to = dictionary.get('recoverTo')
        concurrency = dictionary.get("concurrency") if dictionary.get("concurrency") else 1
        mounts = dictionary.get("mounts") if dictionary.get("mounts") else 1
        recovery_args = dictionary.get('recoveryArgs')
        warnings = dictionary.get('warnings')

        # Return an object of this model
        return cls(snapshots,
                   recover_to,
                   concurrency,
                   mounts,
                   recovery_args,
                   warnings)



# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.backup_schedule_and_retention
import cohesity_management_sdk.models_v2.blackout_window
import cohesity_management_sdk.models_v2.extended_retention_policy
import cohesity_management_sdk.models_v2.targets_configuration
import cohesity_management_sdk.models_v2.retry_options

class ProtectionPolicy(object):

    """Implementation of the 'Protection Policy' model.

    Specifies the details about the Protection Policy.

    Attributes:
        name (string): Specifies the name of the Protection Policy.
        backup_policy (BackupScheduleAndRetention): Specifies the backup
            schedule and retentions of a Protection Policy.
        description (string): Specifies the description of the Protection
            Policy.
        blackout_window (list of BlackoutWindow): List of Blackout Windows. If
            specified, this field defines blackout periods when new Group Runs
            are not started. If a Group Run has been scheduled but not yet
            executed and the blackout period starts, the behavior depends on
            the policy field AbortInBlackoutPeriod.
        extended_retention (list of ExtendedRetentionPolicy): Specifies
            additional retention policies that should be applied to the backup
            snapshots. A backup snapshot will be retained up to a time that is
            the maximum of all retention policies that are applicable to it.
        remote_target_policy (TargetsConfiguration): Specifies the
            replication, archival and cloud spin targets of Protection
            Policy.
        retry_options (RetryOptions): Retry Options of a Protection Policy
            when a Protection Group run fails.
        data_lock (DataLock1Enum): This field is now deprecated. Please use
            the DataLockConfig in the backup retention.
        id (string): Specifies a unique Policy id assigned by the Cohesity
            Cluster.
        num_linked_policies (long|int): Specifies the number of policies
            linked to this policy template. Only applicable in case of policy
            template.
        is_usable (bool): This field is set to true if this policy template
            qualifies to create more policies. If the template is partially
            filled and can not create a working policy then this field will be
            set to false.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "name":'name',
        "backup_policy":'backupPolicy',
        "description":'description',
        "blackout_window":'blackoutWindow',
        "extended_retention":'extendedRetention',
        "remote_target_policy":'remoteTargetPolicy',
        "retry_options":'retryOptions',
        "data_lock":'dataLock',
        "id":'id',
        "num_linked_policies":'numLinkedPolicies',
        "is_usable":'isUsable'
    }

    def __init__(self,
                 name=None,
                 backup_policy=None,
                 description=None,
                 blackout_window=None,
                 extended_retention=None,
                 remote_target_policy=None,
                 retry_options=None,
                 data_lock=None,
                 id=None,
                 num_linked_policies=None,
                 is_usable=None):
        """Constructor for the ProtectionPolicy class"""

        # Initialize members of the class
        self.name = name
        self.backup_policy = backup_policy
        self.description = description
        self.blackout_window = blackout_window
        self.extended_retention = extended_retention
        self.remote_target_policy = remote_target_policy
        self.retry_options = retry_options
        self.data_lock = data_lock
        self.id = id
        self.num_linked_policies = num_linked_policies
        self.is_usable = is_usable


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
        name = dictionary.get('name')
        backup_policy = cohesity_management_sdk.models_v2.backup_schedule_and_retention.BackupScheduleAndRetention.from_dictionary(dictionary.get('backupPolicy')) if dictionary.get('backupPolicy') else None
        description = dictionary.get('description')
        blackout_window = None
        if dictionary.get('blackoutWindow') != None:
            blackout_window = list()
            for structure in dictionary.get('blackoutWindow'):
                blackout_window.append(cohesity_management_sdk.models_v2.blackout_window.BlackoutWindow.from_dictionary(structure))
        extended_retention = None
        if dictionary.get('extendedRetention') != None:
            extended_retention = list()
            for structure in dictionary.get('extendedRetention'):
                extended_retention.append(cohesity_management_sdk.models_v2.extended_retention_policy.ExtendedRetentionPolicy.from_dictionary(structure))
        remote_target_policy = cohesity_management_sdk.models_v2.targets_configuration.TargetsConfiguration.from_dictionary(dictionary.get('remoteTargetPolicy')) if dictionary.get('remoteTargetPolicy') else None
        retry_options = cohesity_management_sdk.models_v2.retry_options.RetryOptions.from_dictionary(dictionary.get('retryOptions')) if dictionary.get('retryOptions') else None
        data_lock = dictionary.get('dataLock')
        id = dictionary.get('id')
        num_linked_policies = dictionary.get('numLinkedPolicies')
        is_usable = dictionary.get('isUsable')

        # Return an object of this model
        return cls(name,
                   backup_policy,
                   description,
                   blackout_window,
                   extended_retention,
                   remote_target_policy,
                   retry_options,
                   data_lock,
                   id,
                   num_linked_policies,
                   is_usable)



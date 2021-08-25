# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.oracle_protection_group_database_node_channel
import cohesity_management_sdk.models_v2.shell_key_value_pair
import cohesity_management_sdk.models_v2.recover_oracle_granular_restore_information

class RecoverViewParams(object):

    """Implementation of the 'RecoverViewParams' model.

    Specifies recovery parameters when recovering to a view.

    Attributes:
        view_mount_path (string): Specifies the directory where cohesity view
            for app recovery will be mounted.
        restore_time_usecs (long|int): Specifies the time in the past to which
            the Oracle db needs to be restored. This allows for granular
            recovery of Oracle databases. If this is not set, the Oracle db
            will be restored from the full/incremental snapshot.
        db_channels (list of OracleProtectionGroupDatabaseNodeChannel):
            Specifies the Oracle database node channels info. If not
            specified, the default values assigned by the server are applied
            to all the databases.
        recovery_mode (bool): Specifies if database should be left in recovery
            mode.
        shell_evironment_vars (list of ShellKeyValuePair): Specifies key value
            pairs of shell variables which defines the restore shell
            environment.
        granular_restore_info (RecoverOracleGranularRestoreInformation):
            Specifies information about list of objects (PDBs) to restore.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "view_mount_path":'viewMountPath',
        "restore_time_usecs":'restoreTimeUsecs',
        "db_channels":'dbChannels',
        "recovery_mode":'recoveryMode',
        "shell_evironment_vars":'shellEvironmentVars',
        "granular_restore_info":'granularRestoreInfo'
    }

    def __init__(self,
                 view_mount_path=None,
                 restore_time_usecs=None,
                 db_channels=None,
                 recovery_mode=None,
                 shell_evironment_vars=None,
                 granular_restore_info=None):
        """Constructor for the RecoverViewParams class"""

        # Initialize members of the class
        self.view_mount_path = view_mount_path
        self.restore_time_usecs = restore_time_usecs
        self.db_channels = db_channels
        self.recovery_mode = recovery_mode
        self.shell_evironment_vars = shell_evironment_vars
        self.granular_restore_info = granular_restore_info


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
        view_mount_path = dictionary.get('viewMountPath')
        restore_time_usecs = dictionary.get('restoreTimeUsecs')
        db_channels = None
        if dictionary.get('dbChannels') != None:
            db_channels = list()
            for structure in dictionary.get('dbChannels'):
                db_channels.append(cohesity_management_sdk.models_v2.oracle_protection_group_database_node_channel.OracleProtectionGroupDatabaseNodeChannel.from_dictionary(structure))
        recovery_mode = dictionary.get('recoveryMode')
        shell_evironment_vars = None
        if dictionary.get('shellEvironmentVars') != None:
            shell_evironment_vars = list()
            for structure in dictionary.get('shellEvironmentVars'):
                shell_evironment_vars.append(cohesity_management_sdk.models_v2.shell_key_value_pair.ShellKeyValuePair.from_dictionary(structure))
        granular_restore_info = cohesity_management_sdk.models_v2.recover_oracle_granular_restore_information.RecoverOracleGranularRestoreInformation.from_dictionary(dictionary.get('granularRestoreInfo')) if dictionary.get('granularRestoreInfo') else None

        # Return an object of this model
        return cls(view_mount_path,
                   restore_time_usecs,
                   db_channels,
                   recovery_mode,
                   shell_evironment_vars,
                   granular_restore_info)



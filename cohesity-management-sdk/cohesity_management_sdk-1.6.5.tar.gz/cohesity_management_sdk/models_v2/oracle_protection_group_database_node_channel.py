# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.oracle_protection_group_database_host

class OracleProtectionGroupDatabaseNodeChannel(object):

    """Implementation of the 'Oracle Protection Group Database Node Channel' model.

    Specifies the DB channel info for all the databases of app entity. Length
    of this array will be 1 for RAC and Standalone setups.

    Attributes:
        archive_log_retention_days (int): Specifies the number of days archive
            log should be stored. For keeping the archived log forever, set
            this to -1. For deleting the archived log immediately, set this to
            0. For deleting the archived log after n days, set this to n.
        database_unique_name (string): Specifies the unique Name of the
            database.
        database_uuid (string): Specifies the database unique id. This is an
            internal field and is filled by magneto master based on
            corresponding app entity id.
        default_channel_count (int): Specifies the default number of channels
            to use per node per database. This value is used on all Oracle
            Database Nodes unless databaseNodeList item's channelCount is
            specified for the node. Default value for the number of channels
            will be calculated as the minimum of number of nodes in Cohesity
            cluster and 2 * number of CPU on the host. If the number of
            channels is unspecified here and unspecified within
            databaseNodeList, the above formula will be used to determine the
            same.
        database_node_list (list of OracleProtectionGroupDatabaseHost):
            Specifies the Node info from where we are allowed to take the
            backup/restore.
        max_host_count (int): Specifies the maximum number of hosts from which
            backup/restore is allowed in parallel. This will be less than or
            equal to the number of databaseNode specified within
            databaseNodeList.
        enable_dg_primary_backup (bool): Specifies whether the database having
            the Primary role within Data Guard configuration is to be backed
            up.
        rman_backup_type (RmanBackupTypeEnum): Specifies the type of Oracle
            RMAN backup requested

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "archive_log_retention_days":'archiveLogRetentionDays',
        "database_unique_name":'databaseUniqueName',
        "database_uuid":'databaseUuid',
        "default_channel_count":'defaultChannelCount',
        "database_node_list":'databaseNodeList',
        "max_host_count":'maxHostCount',
        "enable_dg_primary_backup":'enableDgPrimaryBackup',
        "rman_backup_type":'rmanBackupType'
    }

    def __init__(self,
                 archive_log_retention_days=None,
                 database_unique_name=None,
                 database_uuid=None,
                 default_channel_count=None,
                 database_node_list=None,
                 max_host_count=None,
                 enable_dg_primary_backup=None,
                 rman_backup_type=None):
        """Constructor for the OracleProtectionGroupDatabaseNodeChannel class"""

        # Initialize members of the class
        self.archive_log_retention_days = archive_log_retention_days
        self.database_unique_name = database_unique_name
        self.database_uuid = database_uuid
        self.default_channel_count = default_channel_count
        self.database_node_list = database_node_list
        self.max_host_count = max_host_count
        self.enable_dg_primary_backup = enable_dg_primary_backup
        self.rman_backup_type = rman_backup_type


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
        archive_log_retention_days = dictionary.get('archiveLogRetentionDays')
        database_unique_name = dictionary.get('databaseUniqueName')
        database_uuid = dictionary.get('databaseUuid')
        default_channel_count = dictionary.get('defaultChannelCount')
        database_node_list = None
        if dictionary.get('databaseNodeList') != None:
            database_node_list = list()
            for structure in dictionary.get('databaseNodeList'):
                database_node_list.append(cohesity_management_sdk.models_v2.oracle_protection_group_database_host.OracleProtectionGroupDatabaseHost.from_dictionary(structure))
        max_host_count = dictionary.get('maxHostCount')
        enable_dg_primary_backup = dictionary.get('enableDgPrimaryBackup')
        rman_backup_type = dictionary.get('rmanBackupType')

        # Return an object of this model
        return cls(archive_log_retention_days,
                   database_unique_name,
                   database_uuid,
                   default_channel_count,
                   database_node_list,
                   max_host_count,
                   enable_dg_primary_backup,
                   rman_backup_type)



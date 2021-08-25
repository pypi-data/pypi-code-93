# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.local_snapshot_statistics

class SnapshotInformationForAnObject(object):

    """Implementation of the 'Snapshot information for an object.' model.

    Snapshot info for an object.

    Attributes:
        snapshot_id (string): Snapshot id for a successful snapshot. This
            field will not be set if the Protection Group Run has no
            successful attempt.
        status (Status4Enum): Status of snapshot.
        start_time_usecs (long|int): Specifies the start time of attempt in
            Unix epoch Timestamp(in microseconds) for an object.
        end_time_usecs (long|int): Specifies the end time of attempt in Unix
            epoch Timestamp(in microseconds) for an object.
        admitted_time_usecs (long|int): Specifies the time at which the backup
            task was admitted to run in Unix epoch Timestamp(in microseconds)
            for an object.
        snapshot_creation_time_usecs (long|int): Specifies the time at which
            the source snapshot was taken in Unix epoch Timestamp(in
            microseconds) for an object.
        stats (LocalSnapshotStatistics): Specifies statistics about local
            snapshot.
        progress_task_id (string): Progress monitor task for an object.
        warnings (list of string): Specifies a list of warning messages.
        is_manually_deleted (bool): Specifies whether the snapshot is deleted
            manually.
        expiry_time_usecs (long|int): Specifies the expiry time of attempt in
            Unix epoch Timestamp (in microseconds) for an object.
        total_file_count (long|int): The total number of file and directory
            entities visited in this backup. Only applicable to file based
            backups.
        backup_file_count (long|int): The total number of file and directory
            entities that are backed up in this run. Only applicable to file
            based backups.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "snapshot_id":'snapshotId',
        "status":'status',
        "start_time_usecs":'startTimeUsecs',
        "end_time_usecs":'endTimeUsecs',
        "admitted_time_usecs":'admittedTimeUsecs',
        "snapshot_creation_time_usecs":'snapshotCreationTimeUsecs',
        "stats":'stats',
        "progress_task_id":'progressTaskId',
        "warnings":'warnings',
        "is_manually_deleted":'isManuallyDeleted',
        "expiry_time_usecs":'expiryTimeUsecs',
        "total_file_count":'totalFileCount',
        "backup_file_count":'backupFileCount'
    }

    def __init__(self,
                 snapshot_id=None,
                 status=None,
                 start_time_usecs=None,
                 end_time_usecs=None,
                 admitted_time_usecs=None,
                 snapshot_creation_time_usecs=None,
                 stats=None,
                 progress_task_id=None,
                 warnings=None,
                 is_manually_deleted=None,
                 expiry_time_usecs=None,
                 total_file_count=None,
                 backup_file_count=None):
        """Constructor for the SnapshotInformationForAnObject class"""

        # Initialize members of the class
        self.snapshot_id = snapshot_id
        self.status = status
        self.start_time_usecs = start_time_usecs
        self.end_time_usecs = end_time_usecs
        self.admitted_time_usecs = admitted_time_usecs
        self.snapshot_creation_time_usecs = snapshot_creation_time_usecs
        self.stats = stats
        self.progress_task_id = progress_task_id
        self.warnings = warnings
        self.is_manually_deleted = is_manually_deleted
        self.expiry_time_usecs = expiry_time_usecs
        self.total_file_count = total_file_count
        self.backup_file_count = backup_file_count


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
        snapshot_id = dictionary.get('snapshotId')
        status = dictionary.get('status')
        start_time_usecs = dictionary.get('startTimeUsecs')
        end_time_usecs = dictionary.get('endTimeUsecs')
        admitted_time_usecs = dictionary.get('admittedTimeUsecs')
        snapshot_creation_time_usecs = dictionary.get('snapshotCreationTimeUsecs')
        stats = cohesity_management_sdk.models_v2.local_snapshot_statistics.LocalSnapshotStatistics.from_dictionary(dictionary.get('stats')) if dictionary.get('stats') else None
        progress_task_id = dictionary.get('progressTaskId')
        warnings = dictionary.get('warnings')
        is_manually_deleted = dictionary.get('isManuallyDeleted')
        expiry_time_usecs = dictionary.get('expiryTimeUsecs')
        total_file_count = dictionary.get('totalFileCount')
        backup_file_count = dictionary.get('backupFileCount')

        # Return an object of this model
        return cls(snapshot_id,
                   status,
                   start_time_usecs,
                   end_time_usecs,
                   admitted_time_usecs,
                   snapshot_creation_time_usecs,
                   stats,
                   progress_task_id,
                   warnings,
                   is_manually_deleted,
                   expiry_time_usecs,
                   total_file_count,
                   backup_file_count)



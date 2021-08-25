# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.archival_data_statistics
import cohesity_management_sdk.models_v2.data_lock_constraints

class ArchivalResultForATarget(object):

    """Implementation of the 'Archival result for a target.' model.

    Archival result for an archival target.

    Attributes:
        target_id (long|int): Specifies the archival target ID.
        archival_task_id (string): Specifies the archival task id. This is a
            protection group UID which only applies when archival type is
            'Tape'.
        target_name (string): Specifies the archival target name.
        target_type (TargetType1Enum): Specifies the archival target type.
        snapshot_id (string): Snapshot id for a successful snapshot. This
            field will not be set if the archival Run fails to take the
            snapshot.
        start_time_usecs (long|int): Specifies the start time of replication
            run in Unix epoch Timestamp(in microseconds) for an archival
            target.
        end_time_usecs (long|int): Specifies the end time of replication run
            in Unix epoch Timestamp(in microseconds) for an archival target.
        queued_time_usecs (long|int): Specifies the time when the archival is
            queued for schedule in Unix epoch Timestamp(in microseconds) for a
            target.
        is_incremental (bool): Whether this is an incremental archive. If set
            to true, this is an incremental archive, otherwise this is a full
            archive.
        status (Status2Enum): Status of the replication run for an archival
            target. 'Running' indicates that the run is still running.
            'Canceled' indicates that the run has been canceled. 'Canceling'
            indicates that the run is in the process of being canceled.
            'Failed' indicates that the run has failed. 'Missed' indicates
            that the run was unable to take place at the scheduled time
            because the previous run was still happening. 'Succeeded'
            indicates that the run has finished successfully.
            'SucceededWithWarning' indicates that the run finished
            successfully, but there were some warning messages.
        message (string): Message about the archival run.
        progress_task_id (string): Progress monitor task id for archival.
        stats (ArchivalDataStatistics): Specifies statistics about archival
            data.
        is_manually_deleted (bool): Specifies whether the snapshot is deleted
            manually.
        expiry_time_usecs (long|int): Specifies the expiry time of attempt in
            Unix epoch Timestamp (in microseconds).
        data_lock_constraints (DataLockConstraints): Specifies the dataLock
            constraints for local or target snapshot.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "target_id":'targetId',
        "archival_task_id":'archivalTaskId',
        "target_name":'targetName',
        "target_type":'targetType',
        "snapshot_id":'snapshotId',
        "start_time_usecs":'startTimeUsecs',
        "end_time_usecs":'endTimeUsecs',
        "queued_time_usecs":'queuedTimeUsecs',
        "is_incremental":'isIncremental',
        "status":'status',
        "message":'message',
        "progress_task_id":'progressTaskId',
        "stats":'stats',
        "is_manually_deleted":'isManuallyDeleted',
        "expiry_time_usecs":'expiryTimeUsecs',
        "data_lock_constraints":'dataLockConstraints'
    }

    def __init__(self,
                 target_id=None,
                 archival_task_id=None,
                 target_name=None,
                 target_type=None,
                 snapshot_id=None,
                 start_time_usecs=None,
                 end_time_usecs=None,
                 queued_time_usecs=None,
                 is_incremental=None,
                 status=None,
                 message=None,
                 progress_task_id=None,
                 stats=None,
                 is_manually_deleted=None,
                 expiry_time_usecs=None,
                 data_lock_constraints=None):
        """Constructor for the ArchivalResultForATarget class"""

        # Initialize members of the class
        self.target_id = target_id
        self.archival_task_id = archival_task_id
        self.target_name = target_name
        self.target_type = target_type
        self.snapshot_id = snapshot_id
        self.start_time_usecs = start_time_usecs
        self.end_time_usecs = end_time_usecs
        self.queued_time_usecs = queued_time_usecs
        self.is_incremental = is_incremental
        self.status = status
        self.message = message
        self.progress_task_id = progress_task_id
        self.stats = stats
        self.is_manually_deleted = is_manually_deleted
        self.expiry_time_usecs = expiry_time_usecs
        self.data_lock_constraints = data_lock_constraints


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
        target_id = dictionary.get('targetId')
        archival_task_id = dictionary.get('archivalTaskId')
        target_name = dictionary.get('targetName')
        target_type = dictionary.get('targetType')
        snapshot_id = dictionary.get('snapshotId')
        start_time_usecs = dictionary.get('startTimeUsecs')
        end_time_usecs = dictionary.get('endTimeUsecs')
        queued_time_usecs = dictionary.get('queuedTimeUsecs')
        is_incremental = dictionary.get('isIncremental')
        status = dictionary.get('status')
        message = dictionary.get('message')
        progress_task_id = dictionary.get('progressTaskId')
        stats = cohesity_management_sdk.models_v2.archival_data_statistics.ArchivalDataStatistics.from_dictionary(dictionary.get('stats')) if dictionary.get('stats') else None
        is_manually_deleted = dictionary.get('isManuallyDeleted')
        expiry_time_usecs = dictionary.get('expiryTimeUsecs')
        data_lock_constraints = cohesity_management_sdk.models_v2.data_lock_constraints.DataLockConstraints.from_dictionary(dictionary.get('dataLockConstraints')) if dictionary.get('dataLockConstraints') else None

        # Return an object of this model
        return cls(target_id,
                   archival_task_id,
                   target_name,
                   target_type,
                   snapshot_id,
                   start_time_usecs,
                   end_time_usecs,
                   queued_time_usecs,
                   is_incremental,
                   status,
                   message,
                   progress_task_id,
                   stats,
                   is_manually_deleted,
                   expiry_time_usecs,
                   data_lock_constraints)



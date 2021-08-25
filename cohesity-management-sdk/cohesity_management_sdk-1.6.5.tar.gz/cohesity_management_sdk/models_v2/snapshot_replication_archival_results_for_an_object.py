# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.object_summary
import cohesity_management_sdk.models_v2.snapshot_run_information_for_an_object
import cohesity_management_sdk.models_v2.replication_run_information_for_an_object
import cohesity_management_sdk.models_v2.archival_run_information_for_an_object
import cohesity_management_sdk.models_v2.cloud_spin_run_information_for_an_object

class SnapshotReplicationArchivalResultsForAnObject(object):

    """Implementation of the 'Snapshot, replication, archival results for an object.' model.

    Snapshot, replication, archival results for an object.

    Attributes:
        object (ObjectSummary): Specifies the Object Summary.
        local_snapshot_info (SnapshotRunInformationForAnObject): Specifies
            information about backup run for an object.
        original_backup_info (SnapshotRunInformationForAnObject): Specifies
            information about backup run for an object.
        replication_info (ReplicationRunInformationForAnObject): Specifies
            information about replication run for an object.
        archival_info (ArchivalRunInformationForAnObject): Specifies
            information about archival run for an object.
        cloud_spin_info (CloudSpinRunInformationForAnObject): Specifies
            information about Cloud Spin run for an object.
        on_legal_hold (bool): Specifies if object's snapshot is on legal
            hold.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "object":'object',
        "local_snapshot_info":'localSnapshotInfo',
        "original_backup_info":'originalBackupInfo',
        "replication_info":'replicationInfo',
        "archival_info":'archivalInfo',
        "cloud_spin_info":'cloudSpinInfo',
        "on_legal_hold":'onLegalHold'
    }

    def __init__(self,
                 object=None,
                 local_snapshot_info=None,
                 original_backup_info=None,
                 replication_info=None,
                 archival_info=None,
                 cloud_spin_info=None,
                 on_legal_hold=None):
        """Constructor for the SnapshotReplicationArchivalResultsForAnObject class"""

        # Initialize members of the class
        self.object = object
        self.local_snapshot_info = local_snapshot_info
        self.original_backup_info = original_backup_info
        self.replication_info = replication_info
        self.archival_info = archival_info
        self.cloud_spin_info = cloud_spin_info
        self.on_legal_hold = on_legal_hold


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
        object = cohesity_management_sdk.models_v2.object_summary.ObjectSummary.from_dictionary(dictionary.get('object')) if dictionary.get('object') else None
        local_snapshot_info = cohesity_management_sdk.models_v2.snapshot_run_information_for_an_object.SnapshotRunInformationForAnObject.from_dictionary(dictionary.get('localSnapshotInfo')) if dictionary.get('localSnapshotInfo') else None
        original_backup_info = cohesity_management_sdk.models_v2.snapshot_run_information_for_an_object.SnapshotRunInformationForAnObject.from_dictionary(dictionary.get('originalBackupInfo')) if dictionary.get('originalBackupInfo') else None
        replication_info = cohesity_management_sdk.models_v2.replication_run_information_for_an_object.ReplicationRunInformationForAnObject.from_dictionary(dictionary.get('replicationInfo')) if dictionary.get('replicationInfo') else None
        archival_info = cohesity_management_sdk.models_v2.archival_run_information_for_an_object.ArchivalRunInformationForAnObject.from_dictionary(dictionary.get('archivalInfo')) if dictionary.get('archivalInfo') else None
        cloud_spin_info = cohesity_management_sdk.models_v2.cloud_spin_run_information_for_an_object.CloudSpinRunInformationForAnObject.from_dictionary(dictionary.get('cloudSpinInfo')) if dictionary.get('cloudSpinInfo') else None
        on_legal_hold = dictionary.get('onLegalHold')

        # Return an object of this model
        return cls(object,
                   local_snapshot_info,
                   original_backup_info,
                   replication_info,
                   archival_info,
                   cloud_spin_info,
                   on_legal_hold)



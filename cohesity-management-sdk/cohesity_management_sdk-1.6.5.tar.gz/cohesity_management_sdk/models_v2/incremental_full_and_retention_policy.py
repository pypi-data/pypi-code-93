# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.incremental_backup_schedule_and_retention
import cohesity_management_sdk.models_v2.full_backup_schedule_and_retention
import cohesity_management_sdk.models_v2.retention

class IncrementalFullAndRetentionPolicy(object):

    """Implementation of the 'Incremental, Full and Retention Policy.' model.

    Specifies the Incremental and Full policy settings and also the common
    Retention policy settings."

    Attributes:
        incremental (IncrementalBackupScheduleAndRetention): Specifies
            incremental backup settings for a Protection Group.
        full (FullBackupScheduleAndRetention): Specifies full backup settings
            for a Protection Group.
        retention (Retention): Specifies the retention of a backup.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "retention":'retention',
        "incremental":'incremental',
        "full":'full'
    }

    def __init__(self,
                 retention=None,
                 incremental=None,
                 full=None):
        """Constructor for the IncrementalFullAndRetentionPolicy class"""

        # Initialize members of the class
        self.incremental = incremental
        self.full = full
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
        retention = cohesity_management_sdk.models_v2.retention.Retention.from_dictionary(dictionary.get('retention')) if dictionary.get('retention') else None
        incremental = cohesity_management_sdk.models_v2.incremental_backup_schedule_and_retention.IncrementalBackupScheduleAndRetention.from_dictionary(dictionary.get('incremental')) if dictionary.get('incremental') else None
        full = cohesity_management_sdk.models_v2.full_backup_schedule_and_retention.FullBackupScheduleAndRetention.from_dictionary(dictionary.get('full')) if dictionary.get('full') else None

        # Return an object of this model
        return cls(retention,
                   incremental,
                   full)



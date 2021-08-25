# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.alert_target

class ProtectionGroupAlertingPolicy(object):

    """Implementation of the 'ProtectionGroupAlertingPolicy' model.

    Specifies a policy for alerting users of the status of a Protection
    Group.

    Attributes:
        backup_run_status (list of BackupRunStatusEnum): Specifies the run
            status for which the user would like to receive alerts.
        alert_targets (list of AlertTarget): Specifies a list of targets to
            receive the alerts.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "backup_run_status":'backupRunStatus',
        "alert_targets":'alertTargets'
    }

    def __init__(self,
                 backup_run_status=None,
                 alert_targets=None):
        """Constructor for the ProtectionGroupAlertingPolicy class"""

        # Initialize members of the class
        self.backup_run_status = backup_run_status
        self.alert_targets = alert_targets


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
        backup_run_status = dictionary.get('backupRunStatus')
        alert_targets = None
        if dictionary.get('alertTargets') != None:
            alert_targets = list()
            for structure in dictionary.get('alertTargets'):
                alert_targets.append(cohesity_management_sdk.models_v2.alert_target.AlertTarget.from_dictionary(structure))

        # Return an object of this model
        return cls(backup_run_status,
                   alert_targets)



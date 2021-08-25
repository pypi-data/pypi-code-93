# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.common_recover_object_snapshot_params
import cohesity_management_sdk.models_v2.recover_one_drive_params_2
import cohesity_management_sdk.models_v2.recover_mailbox_params_2
import cohesity_management_sdk.models_v2.recover_public_folders_params

class RecoverOffice365EnvironmentParams(object):

    """Implementation of the 'Recover Office 365 environment params.' model.

    Specifies the recovery options specific to Office 365 environment.

    Attributes:
        objects (list of CommonRecoverObjectSnapshotParams): Specifies the
            list of recover Object parameters.
        recovery_action (RecoveryAction13Enum): Specifies the type of recovery
            action to be performed.
        recover_one_drive_params (RecoverOneDriveParams2): Specifies the
            parameters to recover Office 365 One Drive.
        recover_mailbox_params (RecoverMailboxParams2): Specifies the
            parameters to recover Office 365 Mailbox.
        recover_public_folders_params (RecoverPublicFoldersParams): Specifies
            the parameters to recover Office 365 Public Folders.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "recovery_action":'recoveryAction',
        "objects":'objects',
        "recover_one_drive_params":'recoverOneDriveParams',
        "recover_mailbox_params":'recoverMailboxParams',
        "recover_public_folders_params":'recoverPublicFoldersParams'
    }

    def __init__(self,
                 recovery_action=None,
                 objects=None,
                 recover_one_drive_params=None,
                 recover_mailbox_params=None,
                 recover_public_folders_params=None):
        """Constructor for the RecoverOffice365EnvironmentParams class"""

        # Initialize members of the class
        self.objects = objects
        self.recovery_action = recovery_action
        self.recover_one_drive_params = recover_one_drive_params
        self.recover_mailbox_params = recover_mailbox_params
        self.recover_public_folders_params = recover_public_folders_params


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
        recovery_action = dictionary.get('recoveryAction')
        objects = None
        if dictionary.get('objects') != None:
            objects = list()
            for structure in dictionary.get('objects'):
                objects.append(cohesity_management_sdk.models_v2.common_recover_object_snapshot_params.CommonRecoverObjectSnapshotParams.from_dictionary(structure))
        recover_one_drive_params = cohesity_management_sdk.models_v2.recover_one_drive_params_2.RecoverOneDriveParams2.from_dictionary(dictionary.get('recoverOneDriveParams')) if dictionary.get('recoverOneDriveParams') else None
        recover_mailbox_params = cohesity_management_sdk.models_v2.recover_mailbox_params_2.RecoverMailboxParams2.from_dictionary(dictionary.get('recoverMailboxParams')) if dictionary.get('recoverMailboxParams') else None
        recover_public_folders_params = cohesity_management_sdk.models_v2.recover_public_folders_params.RecoverPublicFoldersParams.from_dictionary(dictionary.get('recoverPublicFoldersParams')) if dictionary.get('recoverPublicFoldersParams') else None

        # Return an object of this model
        return cls(recovery_action,
                   objects,
                   recover_one_drive_params,
                   recover_mailbox_params,
                   recover_public_folders_params)



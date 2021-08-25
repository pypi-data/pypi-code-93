# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.common_recover_object_snapshot_params
import cohesity_management_sdk.models_v2.recover_sql_db_params
import cohesity_management_sdk.models_v2.download_file_and_folder_params

class RecoverSqlEnvironmentParams(object):

    """Implementation of the 'Recover Sql environment params.' model.

    Specifies the recovery options specific to Sql environment.

    Attributes:
        objects (list of CommonRecoverObjectSnapshotParams): Specifies the
            list of parameters for list of objects to be recovered.
        recovery_action (string): Specifies the type of recover action to be
            performed.
        recover_app_params (RecoverSqlDBParams): Specifies the parameters to
            recover Sql databases.
        download_file_and_folder_params (DownloadFileAndFolderParams):
            Specifies the parameters to download files and folders.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "objects":'objects',
        "recovery_action":'recoveryAction',
        "recover_app_params":'recoverAppParams',
        "download_file_and_folder_params":'downloadFileAndFolderParams'
    }

    def __init__(self,
                 objects=None,
                 recovery_action='RecoverApps',
                 recover_app_params=None,
                 download_file_and_folder_params=None):
        """Constructor for the RecoverSqlEnvironmentParams class"""

        # Initialize members of the class
        self.objects = objects
        self.recovery_action = recovery_action
        self.recover_app_params = recover_app_params
        self.download_file_and_folder_params = download_file_and_folder_params


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
        objects = None
        if dictionary.get('objects') != None:
            objects = list()
            for structure in dictionary.get('objects'):
                objects.append(cohesity_management_sdk.models_v2.common_recover_object_snapshot_params.CommonRecoverObjectSnapshotParams.from_dictionary(structure))
        recovery_action = dictionary.get("recoveryAction") if dictionary.get("recoveryAction") else 'RecoverApps'
        recover_app_params = cohesity_management_sdk.models_v2.recover_sql_db_params.RecoverSqlDBParams.from_dictionary(dictionary.get('recoverAppParams')) if dictionary.get('recoverAppParams') else None
        download_file_and_folder_params = cohesity_management_sdk.models_v2.download_file_and_folder_params.DownloadFileAndFolderParams.from_dictionary(dictionary.get('downloadFileAndFolderParams')) if dictionary.get('downloadFileAndFolderParams') else None

        # Return an object of this model
        return cls(objects,
                   recovery_action,
                   recover_app_params,
                   download_file_and_folder_params)



# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.pre_post_script_host
import cohesity_management_sdk.models_v2.common_pre_backup_script_params
import cohesity_management_sdk.models_v2.common_pre_post_script_params

class HostBasedBackupScriptParams(object):

    """Implementation of the 'Host Based Backup Script Params' model.

    Specifies params of a pre/post scripts to be executed before and after a
    backup run.

    Attributes:
        host (PrePostScriptHost): Specifies the params for the host of a pre /
            post script.
        pre_script (CommonPreBackupScriptParams): Specifies the common params
            for PreBackup scripts.
        post_script (CommonPrePostScriptParams): Specifies the common params
            for PostBackup scripts.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "host":'host',
        "pre_script":'preScript',
        "post_script":'postScript'
    }

    def __init__(self,
                 host=None,
                 pre_script=None,
                 post_script=None):
        """Constructor for the HostBasedBackupScriptParams class"""

        # Initialize members of the class
        self.host = host
        self.pre_script = pre_script
        self.post_script = post_script


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
        host = cohesity_management_sdk.models_v2.pre_post_script_host.PrePostScriptHost.from_dictionary(dictionary.get('host')) if dictionary.get('host') else None
        pre_script = cohesity_management_sdk.models_v2.common_pre_backup_script_params.CommonPreBackupScriptParams.from_dictionary(dictionary.get('preScript')) if dictionary.get('preScript') else None
        post_script = cohesity_management_sdk.models_v2.common_pre_post_script_params.CommonPrePostScriptParams.from_dictionary(dictionary.get('postScript')) if dictionary.get('postScript') else None

        # Return an object of this model
        return cls(host,
                   pre_script,
                   post_script)



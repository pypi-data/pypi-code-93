# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.smb_mount_credentials
import cohesity_management_sdk.models_v2.nas_source_and_protection_throttling_configuration

class FlashbladeProtectionSource(object):

    """Implementation of the 'Flashblade Protection Source.' model.

    Specifies parameters to register an Flashblade Source.

    Attributes:
        endpoint (string): Specifies the Hostname or IP Address Endpoint for
            the Flashblade Source.
        api_token (string): Specifies the API Token of the Flashblade Source
        back_up_smb_volumes (bool): Specifies whether or not to back up SMB
            Volumes.
        smb_credentials (SMBMountCredentials): Specifies the credentials to
            mount a view.
        throttling_config (NasSourceAndProtectionThrottlingConfiguration):
            Specifies the source throttling parameters to be used during full
            or incremental backup of the NAS source.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "endpoint":'endpoint',
        "api_token":'apiToken',
        "back_up_smb_volumes":'backUpSMBVolumes',
        "smb_credentials":'smbCredentials',
        "throttling_config":'throttlingConfig'
    }

    def __init__(self,
                 endpoint=None,
                 api_token=None,
                 back_up_smb_volumes=None,
                 smb_credentials=None,
                 throttling_config=None):
        """Constructor for the FlashbladeProtectionSource class"""

        # Initialize members of the class
        self.endpoint = endpoint
        self.api_token = api_token
        self.back_up_smb_volumes = back_up_smb_volumes
        self.smb_credentials = smb_credentials
        self.throttling_config = throttling_config


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
        endpoint = dictionary.get('endpoint')
        api_token = dictionary.get('apiToken')
        back_up_smb_volumes = dictionary.get('backUpSMBVolumes')
        smb_credentials = cohesity_management_sdk.models_v2.smb_mount_credentials.SMBMountCredentials.from_dictionary(dictionary.get('smbCredentials')) if dictionary.get('smbCredentials') else None
        throttling_config = cohesity_management_sdk.models_v2.nas_source_and_protection_throttling_configuration.NasSourceAndProtectionThrottlingConfiguration.from_dictionary(dictionary.get('throttlingConfig')) if dictionary.get('throttlingConfig') else None

        # Return an object of this model
        return cls(endpoint,
                   api_token,
                   back_up_smb_volumes,
                   smb_credentials,
                   throttling_config)



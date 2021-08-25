# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.alias_smb_config
import cohesity_management_sdk.models_v2.subnet

class ViewAliasInformation(object):

    """Implementation of the 'View Alias Information.' model.

    View Alias Info is returned as part of list views.

    Attributes:
        alias_name (string): Alias name.
        view_path (string): View path for the alias.
        smb_config (AliasSmbConfig): Message defining SMB config for IRIS. SMB
            config contains SMB encryption flags, SMB discoverable flag and
            Share level permissions.
        client_subnet_whitelist (list of Subnet): List of external client
            subnet IPs that are allowed to access the share.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "alias_name":'aliasName',
        "view_path":'viewPath',
        "smb_config":'smbConfig',
        "client_subnet_whitelist":'clientSubnetWhitelist'
    }

    def __init__(self,
                 alias_name=None,
                 view_path=None,
                 smb_config=None,
                 client_subnet_whitelist=None):
        """Constructor for the ViewAliasInformation class"""

        # Initialize members of the class
        self.alias_name = alias_name
        self.view_path = view_path
        self.smb_config = smb_config
        self.client_subnet_whitelist = client_subnet_whitelist


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
        alias_name = dictionary.get('aliasName')
        view_path = dictionary.get('viewPath')
        smb_config = cohesity_management_sdk.models_v2.alias_smb_config.AliasSmbConfig.from_dictionary(dictionary.get('smbConfig')) if dictionary.get('smbConfig') else None
        client_subnet_whitelist = None
        if dictionary.get('clientSubnetWhitelist') != None:
            client_subnet_whitelist = list()
            for structure in dictionary.get('clientSubnetWhitelist'):
                client_subnet_whitelist.append(cohesity_management_sdk.models_v2.subnet.Subnet.from_dictionary(structure))

        # Return an object of this model
        return cls(alias_name,
                   view_path,
                   smb_config,
                   client_subnet_whitelist)



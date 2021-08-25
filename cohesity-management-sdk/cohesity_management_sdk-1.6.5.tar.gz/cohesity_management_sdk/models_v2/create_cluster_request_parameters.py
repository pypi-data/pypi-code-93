# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.cluster_network_config
import cohesity_management_sdk.models_v2.physical_cluster_params
import cohesity_management_sdk.models_v2.virtual_cluster_params
import cohesity_management_sdk.models_v2.cloud_cluster_params

class CreateClusterRequestParameters(object):

    """Implementation of the 'Create Cluster Request Parameters.' model.

    Specifies the parameters required to create cluster.

    Attributes:
        name (string): Specifies the name of the new cluster.
        mtype (Type6Enum): Specifies the type of the new cluster.
        enable_encryption (bool): Specifies whether or not to enable
            encryption. If encryption is enabled, all data on the Cluster will
            be encrypted. This can only be enabled at Cluster creation time
            and cannot be disabled later.
        network_config (ClusterNetworkConfig): Specifies all of the parameters
            needed for network configuration of the new Cluster.
        physical_cluster_params (PhysicalClusterParams): Params for Physical
            Edition Cluster Creation
        virtual_cluster_params (VirtualClusterParams): Params for Virtual
            Edition Cluster Creation
        cloud_cluster_params (CloudClusterParams): Params for Cloud Edition
            Cluster Creation

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "name":'name',
        "mtype":'type',
        "enable_encryption":'enableEncryption',
        "network_config":'networkConfig',
        "physical_cluster_params":'physicalClusterParams',
        "virtual_cluster_params":'virtualClusterParams',
        "cloud_cluster_params":'cloudClusterParams'
    }

    def __init__(self,
                 name=None,
                 mtype=None,
                 enable_encryption=None,
                 network_config=None,
                 physical_cluster_params=None,
                 virtual_cluster_params=None,
                 cloud_cluster_params=None):
        """Constructor for the CreateClusterRequestParameters class"""

        # Initialize members of the class
        self.name = name
        self.mtype = mtype
        self.enable_encryption = enable_encryption
        self.network_config = network_config
        self.physical_cluster_params = physical_cluster_params
        self.virtual_cluster_params = virtual_cluster_params
        self.cloud_cluster_params = cloud_cluster_params


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
        name = dictionary.get('name')
        mtype = dictionary.get('type')
        enable_encryption = dictionary.get('enableEncryption')
        network_config = cohesity_management_sdk.models_v2.cluster_network_config.ClusterNetworkConfig.from_dictionary(dictionary.get('networkConfig')) if dictionary.get('networkConfig') else None
        physical_cluster_params = cohesity_management_sdk.models_v2.physical_cluster_params.PhysicalClusterParams.from_dictionary(dictionary.get('physicalClusterParams')) if dictionary.get('physicalClusterParams') else None
        virtual_cluster_params = cohesity_management_sdk.models_v2.virtual_cluster_params.VirtualClusterParams.from_dictionary(dictionary.get('virtualClusterParams')) if dictionary.get('virtualClusterParams') else None
        cloud_cluster_params = cohesity_management_sdk.models_v2.cloud_cluster_params.CloudClusterParams.from_dictionary(dictionary.get('cloudClusterParams')) if dictionary.get('cloudClusterParams') else None

        # Return an object of this model
        return cls(name,
                   mtype,
                   enable_encryption,
                   network_config,
                   physical_cluster_params,
                   virtual_cluster_params,
                   cloud_cluster_params)



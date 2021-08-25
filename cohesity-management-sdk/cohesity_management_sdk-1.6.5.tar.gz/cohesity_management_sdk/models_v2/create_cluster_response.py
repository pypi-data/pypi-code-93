# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.cluster_network_config
import cohesity_management_sdk.models_v2.node_specific_response

class CreateClusterResponse(object):

    """Implementation of the 'Create Cluster Response.' model.

    Specifies the cluster details.

    Attributes:
        id (long|int): Specifies the cluster id of the new cluster.
        name (string): Name of the new cluster.
        mtype (Type6Enum): Specifies the type of the new cluster.
        sw_version (string): Software version of the new cluster.
        network_config (ClusterNetworkConfig): Specifies all of the parameters
            needed for network configuration of the new Cluster.
        enable_encryption (bool): Specifies whether or not encryption is
            enabled. If encryption is enabled, all data on the Cluster will be
            encrypted.
        healthy_nodes (list of NodeSpecificResponse): List of healthy nodes in
            cluster.
        unhealthy_nodes (list of NodeSpecificResponse): List of unhealthy
            nodes in cluster.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "id":'id',
        "name":'name',
        "mtype":'type',
        "sw_version":'swVersion',
        "network_config":'networkConfig',
        "enable_encryption":'enableEncryption',
        "healthy_nodes":'healthyNodes',
        "unhealthy_nodes":'unhealthyNodes'
    }

    def __init__(self,
                 id=None,
                 name=None,
                 mtype=None,
                 sw_version=None,
                 network_config=None,
                 enable_encryption=None,
                 healthy_nodes=None,
                 unhealthy_nodes=None):
        """Constructor for the CreateClusterResponse class"""

        # Initialize members of the class
        self.id = id
        self.name = name
        self.mtype = mtype
        self.sw_version = sw_version
        self.network_config = network_config
        self.enable_encryption = enable_encryption
        self.healthy_nodes = healthy_nodes
        self.unhealthy_nodes = unhealthy_nodes


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
        id = dictionary.get('id')
        name = dictionary.get('name')
        mtype = dictionary.get('type')
        sw_version = dictionary.get('swVersion')
        network_config = cohesity_management_sdk.models_v2.cluster_network_config.ClusterNetworkConfig.from_dictionary(dictionary.get('networkConfig')) if dictionary.get('networkConfig') else None
        enable_encryption = dictionary.get('enableEncryption')
        healthy_nodes = None
        if dictionary.get('healthyNodes') != None:
            healthy_nodes = list()
            for structure in dictionary.get('healthyNodes'):
                healthy_nodes.append(cohesity_management_sdk.models_v2.node_specific_response.NodeSpecificResponse.from_dictionary(structure))
        unhealthy_nodes = None
        if dictionary.get('unhealthyNodes') != None:
            unhealthy_nodes = list()
            for structure in dictionary.get('unhealthyNodes'):
                unhealthy_nodes.append(cohesity_management_sdk.models_v2.node_specific_response.NodeSpecificResponse.from_dictionary(structure))

        # Return an object of this model
        return cls(id,
                   name,
                   mtype,
                   sw_version,
                   network_config,
                   enable_encryption,
                   healthy_nodes,
                   unhealthy_nodes)



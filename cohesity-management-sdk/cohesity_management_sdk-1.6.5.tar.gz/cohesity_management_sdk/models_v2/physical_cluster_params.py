# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.node_specific_params

class PhysicalClusterParams(object):

    """Implementation of the 'Physical Cluster Params.' model.

    Params for Physical Edition Cluster Creation

    Attributes:
        nodes (list of NodeSpecificParams): TODO: type description here.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "nodes":'nodes'
    }

    def __init__(self,
                 nodes=None):
        """Constructor for the PhysicalClusterParams class"""

        # Initialize members of the class
        self.nodes = nodes


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
        nodes = None
        if dictionary.get('nodes') != None:
            nodes = list()
            for structure in dictionary.get('nodes'):
                nodes.append(cohesity_management_sdk.models_v2.node_specific_params.NodeSpecificParams.from_dictionary(structure))

        # Return an object of this model
        return cls(nodes)



# -*- coding: utf-8 -*-


class RigelClusterNode(object):

    """Implementation of the 'Rigel Cluster Node' model.

    Params for a Rigel Cluster Node

    Attributes:
        node_ip (string): Specifies the IP address of the Node.
        node_id (long|int): Specifies the ID of the Node.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "node_ip":'nodeIp',
        "node_id":'nodeId'
    }

    def __init__(self,
                 node_ip=None,
                 node_id=None):
        """Constructor for the RigelClusterNode class"""

        # Initialize members of the class
        self.node_ip = node_ip
        self.node_id = node_id


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
        node_ip = dictionary.get('nodeIp')
        node_id = dictionary.get('nodeId')

        # Return an object of this model
        return cls(node_ip,
                   node_id)



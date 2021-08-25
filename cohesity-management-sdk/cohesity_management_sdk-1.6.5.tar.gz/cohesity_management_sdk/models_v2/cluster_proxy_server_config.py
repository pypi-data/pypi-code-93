# -*- coding: utf-8 -*-


class ClusterProxyServerConfig(object):

    """Implementation of the 'Cluster Proxy Server Config.' model.

    Specifies the parameters of the proxy server to be used for external
    traffic.

    Attributes:
        name (string): Specifies the unique name of the proxy server.
        ip (string): Specifies the IP address of the proxy server.
        port (int): Specifies the port on which the server is listening.
        username (string): Specifies the username for the proxy.
        password (string): Specifies the password for the proxy.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "ip":'ip',
        "port":'port',
        "name":'name',
        "username":'username',
        "password":'password'
    }

    def __init__(self,
                 ip=None,
                 port=None,
                 name=None,
                 username=None,
                 password=None):
        """Constructor for the ClusterProxyServerConfig class"""

        # Initialize members of the class
        self.name = name
        self.ip = ip
        self.port = port
        self.username = username
        self.password = password


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
        ip = dictionary.get('ip')
        port = dictionary.get('port')
        name = dictionary.get('name')
        username = dictionary.get('username')
        password = dictionary.get('password')

        # Return an object of this model
        return cls(ip,
                   port,
                   name,
                   username,
                   password)



# -*- coding: utf-8 -*-


class ClusterNetworkConfig(object):

    """Implementation of the 'Cluster Network Config.' model.

    Specifies all of the parameters needed for network configuration of the
    new Cluster.

    Attributes:
        gateway (string): Specifies the gateway of the new cluster network.
        subnet_mask (string): Specifies the ip subnet mask of the cluster
            network.
        dns_servers (list of string): Specifies the list of Dns Servers new
            cluster should be configured with.
        ntp_servers (list of string): Specifies the list of NTP Servers new
            cluster should be configured with.
        ip_preference (IpPreferenceEnum): Specifies IP preference of the
            cluster to be Ipv4/Ipv6. It is Ipv4 by default.
        vip_host_name (string): Specifies the FQDN hostname of the cluster.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "gateway":'gateway',
        "subnet_mask":'subnetMask',
        "dns_servers":'dnsServers',
        "ntp_servers":'ntpServers',
        "ip_preference":'ipPreference',
        "vip_host_name":'vipHostName'
    }

    def __init__(self,
                 gateway=None,
                 subnet_mask=None,
                 dns_servers=None,
                 ntp_servers=None,
                 ip_preference=None,
                 vip_host_name=None):
        """Constructor for the ClusterNetworkConfig class"""

        # Initialize members of the class
        self.gateway = gateway
        self.subnet_mask = subnet_mask
        self.dns_servers = dns_servers
        self.ntp_servers = ntp_servers
        self.ip_preference = ip_preference
        self.vip_host_name = vip_host_name


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
        gateway = dictionary.get('gateway')
        subnet_mask = dictionary.get('subnetMask')
        dns_servers = dictionary.get('dnsServers')
        ntp_servers = dictionary.get('ntpServers')
        ip_preference = dictionary.get('ipPreference')
        vip_host_name = dictionary.get('vipHostName')

        # Return an object of this model
        return cls(gateway,
                   subnet_mask,
                   dns_servers,
                   ntp_servers,
                   ip_preference,
                   vip_host_name)



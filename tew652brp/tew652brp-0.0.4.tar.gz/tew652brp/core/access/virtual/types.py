class VServerInfo:
    NODES = {
        'name': 'vsRule_VirtualServerName_',
        'internal_ip': 'vsRule_InternalIPAddr_',
        'enabled': 'vsRule_Enable_',
        'protocol': 'vsRule_Protocol_',
        'public_port': 'vsRule_PublicPort_',
        'private_port': 'vsRule_PrivatePort_',
    }

    __slots__ = ('instance', 'name', 'internal_ip', 'enabled', 'protocol', 'public_port', 'private_port')

    def __init__(self, instance, name, internal_ip, enabled, protocol, public_port, private_port):
        self.instance = instance
        self.name = name
        self.internal_ip = internal_ip
        self.enabled = enabled
        self.protocol = protocol
        self.public_port = public_port
        self.private_port = private_port

    def to_dict(self):
        nodes = {k: f'{self.NODES[k]}{self.instance}' for k in self.NODES.keys()}

        return {
            nodes['name']: self.name,
            nodes['internal_ip']: self.internal_ip,
            nodes['enabled']: self.enabled,
            nodes['protocol']: self.protocol,
            nodes['public_port']: self.public_port,
            nodes['private_port']: self.private_port,
        }

    @classmethod
    def from_xml(cls, xml):
        info = {key: xml.find(node).text for key, node in zip(cls.NODES.keys(), cls.NODES.values())}
        info['instance'] = xml.get('inst').replace(',', '.')
        return cls(**info)

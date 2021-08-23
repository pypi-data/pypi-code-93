from .clients import clb_client

class TencentClb:
    def __init__(self, object):
        self.object = object

    @classmethod
    def get(cls, id):
        lb_set = clb_client.describe_load_balancers(LoadBalancerIds=[id]).get('LoadBalancerSet')
        if len(lb_set) == 0:
            return None
        else:
            return cls(lb_set[0])

    @classmethod
    def list(cls, ids=None):
        params = {}
        if ids:
            params['LoadBalancerIds'] = ids
        lb_set = clb_client.describe_load_balancers(**params).get('LoadBalancerSet')
        return [cls(lb) for lb in lb_set]

    @classmethod
    def create(cls, **params):
        slb_id = clb_client.create_load_balancers(**params)
        return slb_id

    def delete(self):
        clb_client.delete_load_balancers(LoadBalancerIds=[self.external_id])

    def create_listener(self, **kwargs):
        listener_id = clb_client.create_listener(LoadBalancerId=self.external_id, **kwargs)
        return listener_id

    def delete_listener(self, listener_id):
        clb_client.delete_listener(LoadBalancerId=self.external_id, ListenerId=listener_id)

    @property
    def external_id(self):
        return self.object.get('LoadBalancerId')

    @property
    def external_name(self):
        return self.object.get('LoadBalancerName')

    @property
    def network_type(self):
        TYPE_MAPPER = {
            'OPEN': 'public',
            'INTERNAL': 'internal'
        }
        return TYPE_MAPPER[self.object.get('LoadBalancerType')]

    @property
    def charge_type(self):
        return self.object.get('ChargeType')

    @property
    def vpc_id(self):
        return self.object.get('VpcId')

    @property
    def subnet_id(self):
        return self.object.get('SubnetId')

    @property
    def vips(self):
        return ', '.join(self.object.get('LoadBalancerVips'))

    @property
    def status(self):
        mapper = {
            0: "creating",
            1: "started"
        }
        return mapper[self.object.get('Status')]

    @property
    def listeners(self):
        listeners = clb_client.describe_listeners(LoadBalancerId=self.external_id).get('Listeners')
        return [TencentClbListener(self.external_id, listener) for listener in listeners]

    @property
    def band_width(self):
        return self.object.get('NetworkAttributes', {}).get('InternetMaxBandwidthOut')

    def fresh(self):
        self.object = self.get(self.external_id).object

    def __repr__(self):
        return "<TencentClb object:{}>".format(self.external_id)


class TencentClbListener:
    def __init__(self, slb_id, object):
        self.object = object
        self.load_balancer_id = slb_id

    @classmethod
    def get(cls, slb_id, listener_id):
        listener = clb_client.describe_listeners(LoadBalancerId=slb_id, ListenerIds=[listener_id]).get('Listeners')
        if not listener:
            return None
        else:
            return cls(slb_id, listener[0])

    def add_member(self, **kwargs):
        clb_client.add_member(LoadBalancerId=self.load_balancer_id, ListenerId=self.external_id, **kwargs)

    def del_member(self, **kwargs):
        clb_client.del_member(LoadBalancerId=self.load_balancer_id, ListenerId=self.external_id, **kwargs)

    @property
    def external_id(self):
        return self.object.get('ListenerId')

    @property
    def external_name(self):
        return self.object.get('ListenerName')

    @property
    def listener_port(self):
        return self.object.get('Port')

    @property
    def listener_protocol(self):
        return self.object.get('Protocol')

    @property
    def members(self):
        targets = \
            clb_client.describe_members(LoadBalancerId=self.load_balancer_id, ListenerIds=[self.external_id])[
                'Listeners'][0][
                'Targets']
        return [TencentClbListenerMember(target) for target in targets]

    def delete(self):
        clb_client.delete_listener(LoadBalancerId=self.load_balancer_id, ListenerId=self.external_id)

    def __repr__(self):
        return "<TencentClbListener object:{}>".format(self.external_id)


class TencentClbListenerMember:
    def __init__(self, object):
        self.object = object

    @property
    def type(self):
        return self.object.get('Type')

    @property
    def name(self):
        return self.object.get('InstanceName')

    @property
    def port(self):
        return self.object.get('Port')

    @property
    def weight(self):
        return self.object.get('Weight')

    @property
    def instance_id(self):
        return self.object.get('InstanceId')

    @property
    def instance_name(self):
        return self.object.get('InstanceName')

    @property
    def private_ips(self):
        return ', '.join(self.object.get('PrivateIpAddresses'))


from .clients import hw_vpc_client


class HuaweiVpc:

    def __init__(self, object):
        self.object = object

    @property
    def id(self):
        return self.object.id

    @property
    def name(self):
        return self.object.name

    @property
    def cidr(self):
        return self.object.cidr

    @classmethod
    def get(cls, vpc_id=None):
        vpcs = hw_vpc_client.list_vpc(vpc_id)
        if not vpcs:
            return
        return cls(vpcs[0])


class HuaweiSubnet:

    def __init__(self, object):
        self.object = object

    @property
    def id(self):
        return self.object.id

    @property
    def name(self):
        return self.object.name

    @property
    def vpc_id(self):
        return self.object.vpc_id

    @property
    def availability_zone(self):
        return self.object.availability_zone

    @property
    def cidr(self):
        return self.object.cidr

    @property
    def dns_list(self):
        return self.object.dns_list

    @classmethod
    def get(cls, vpc_id=None, subnet_id=None):
        subnets = hw_vpc_client.list_subnet(vpc_id)
        if not subnets:
            return
        for subnet in subnets:
            if subnet.id == subnet_id:
                return cls(subnet)

    @classmethod
    def create(cls, params=None):
        create_response = hw_vpc_client.create_subnet(body_params=params)
        if not create_response:
            return
        return create_response.subnet

    def delete(self):
        return hw_vpc_client.delete_subnet(vpc_id=self.vpc_id, subnet_id=self.id)


class HuaweiSecurityGroup:

    def __init__(self, object):
        self.object = object

    @property
    def id(self):
        return self.object.id

    @property
    def name(self):
        return self.object.name

    @property
    def rules(self):
        all_rules = hw_vpc_client.list_securitygroup_rules(security_group_id=self.id)
        return [HuaweiSecurityGroupRule(rule) for rule in all_rules]

    @classmethod
    def get(cls, sg_id=None):
        sg = hw_vpc_client.show_securitygroup(security_group_id=sg_id)
        return cls(sg)

    @classmethod
    def create(cls, params=None):
        create_response = hw_vpc_client.create_securitygroup(body_params=params)
        if not create_response:
            return
        return create_response.id

    def delete(self):
        return hw_vpc_client.delete_securitygroup(security_group_id=self.id)


class HuaweiSecurityGroupRule:

    def __init__(self, object):
        self.object = object

    @property
    def id(self):
        return self.object.id

    @property
    def direction(self):
        return self.object.direction

    @property
    def protocol(self):
        return self.object.protocol

    @property
    def description(self):
        return self.object.description

    @property
    def cidr(self):
        return self.object.remote_ip_prefix

    @property
    def port(self):
        if not self.object.port_range_min:
            return ""
        return "-".join([str(self.object.port_range_min), str(self.object.port_range_max)])

    @classmethod
    def get(cls, sg_rule_id=None):
        sg_rule = hw_vpc_client.show_securitygroup_rules(security_group_rule_id=sg_rule_id)
        return cls(sg_rule)

    @classmethod
    def create(cls, params=None):
        create_response = hw_vpc_client.create_securitygroup_rule(body_params=params)
        if not create_response:
            return
        return create_response.id

    def delete(self):
        return hw_vpc_client.delete_securitygroup_rule(security_group_rule_id=self.id)




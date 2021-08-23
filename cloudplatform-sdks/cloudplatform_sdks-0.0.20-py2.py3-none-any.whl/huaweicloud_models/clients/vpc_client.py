from .client import HuaweiClient
from huaweicloudsdkvpc.v2 import VpcClient, ListVpcsRequest, ListSubnetsRequest, CreateSubnetRequest, \
    DeleteSubnetRequest, CreateSecurityGroupRequest, DeleteSecurityGroupRequest, ShowSecurityGroupRequest, \
    CreateSecurityGroupRuleRequest, DeleteSecurityGroupRuleRequest, ListSecurityGroupRulesRequest, \
    ShowSecurityGroupRuleRequest
from huaweicloudsdkvpc.v2.region.vpc_region import VpcRegion


class HuaweiVpcClient(HuaweiClient):
    def __init__(self, *args, **kwargs):
        super(HuaweiVpcClient, self).__init__(*args, **kwargs)

    @property
    def vpc_client(self):
        return self.generate_client(VpcClient, VpcRegion)

    def list_vpc(self, vpc_id=None):
        request = ListVpcsRequest(id=vpc_id)
        return self.vpc_client.list_vpcs(request).vpcs

    def list_subnet(self, vpc_id=None):
        request = ListSubnetsRequest(vpc_id=vpc_id)
        return self.vpc_client.list_subnets(request).subnets

    def create_subnet(self, body_params=None):
        request = CreateSubnetRequest(body=body_params)
        return self.vpc_client.create_subnet(request)

    def delete_subnet(self, vpc_id=None, subnet_id=None):
        request = DeleteSubnetRequest(vpc_id=vpc_id, subnet_id=subnet_id)
        return self.vpc_client.delete_subnet(request)

    def create_securitygroup(self, body_params=None):
        request = CreateSecurityGroupRequest(body=body_params)
        return self.vpc_client.create_security_group(request).security_group

    def delete_securitygroup(self, security_group_id=None):
        request = DeleteSecurityGroupRequest(security_group_id=security_group_id)
        return self.vpc_client.delete_security_group(request)

    def show_securitygroup(self, security_group_id=None):
        request = ShowSecurityGroupRequest(security_group_id=security_group_id)
        return self.vpc_client.show_security_group(request).security_group

    def create_securitygroup_rule(self, body_params=None):
        request = CreateSecurityGroupRuleRequest(body=body_params)
        return self.vpc_client.create_security_group_rule(request).security_group_rule

    def delete_securitygroup_rule(self, security_group_rule_id=None):
        request = DeleteSecurityGroupRuleRequest(security_group_rule_id=security_group_rule_id)
        return self.vpc_client.delete_security_group_rule(request)

    def list_securitygroup_rules(self, security_group_id=None):
        request = ListSecurityGroupRulesRequest(security_group_id=security_group_id)
        return self.vpc_client.list_security_group_rules(request).security_group_rules

    def show_securitygroup_rules(self, security_group_rule_id=None):
        request = ShowSecurityGroupRuleRequest(security_group_rule_id=security_group_rule_id)
        return self.vpc_client.show_security_group_rule(request).security_group_rule

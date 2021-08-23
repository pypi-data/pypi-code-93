from .client import TencentClient
from tencentcloud.vpc.v20170312 import vpc_client as tencent_vpc_client
from tencentcloud.vpc.v20170312 import models


class VpcClient(TencentClient):
    def __init__(self, *args, **kwargs):
        super(VpcClient, self).__init__(*args, **kwargs)
        self.httpProfile.endpoint = "vpc.tencentcloudapi.com"
        self.clientProfile.httpProfile = self.httpProfile
        self.client = tencent_vpc_client.VpcClient(self.cred, self.region, self.clientProfile)

    # subnet
    def create_subnet(self, **kwargs):
        req = models.CreateSubnetRequest()
        return self.do_request(self.client.CreateSubnet, req, **kwargs)

    def delete_subnet(self, **kwargs):
        req = models.DeleteSubnetRequest()
        return self.do_request(self.client.DeleteSubnet, req, **kwargs)

    def describe_subnet(self, **kwargs):
        req = models.DescribeSubnetsRequest()
        return self.do_request(self.client.DescribeSubnets, req, **kwargs)

    # route table
    def create_route_table(self, **kwargs):
        req = models.CreateRouteTableRequest()
        res = self.do_request(self.client.CreateRouteTable, req, **kwargs)
        return res['RouteTable']['RouteTableId']

    def delete_route_table(self, **kwargs):
        req = models.DeleteRouteTableRequest()
        return self.do_request(self.client.DeleteRouteTable, req, **kwargs)

    def describe_route_table(self, **kwargs):
        req = models.DescribeRouteTablesRequest()
        return self.do_request(self.client.DescribeRouteTables, req, **kwargs)

    def replace_route_table_associated_subnet(self, **kwargs):
        req = models.ReplaceRouteTableAssociationRequest()
        return self.do_request(self.client.ReplaceRouteTableAssociation, req, **kwargs)

    # route entry -> routes
    def create_route_entry(self, **kwargs):
        req = models.CreateRoutesRequest()
        return self.do_request(self.client.CreateRoutes, req, **kwargs)

    def delete_route_entry(self, **kwargs):
        req = models.DeleteRoutesRequest()
        return self.do_request(self.client.DeleteRoutes, req, **kwargs)

    def describe_route_entry(self, **kwargs):
        req = models.DescribeRouteTablesRequest()
        return self.do_request(self.client.DescribeRouteTables, req, **kwargs)

    # nas
    def describe_nas(self, **kwargs):
        req = models.DescribeNatGatewaysRequest()
        return self.do_request(self.client.DescribeNatGateways, req, **kwargs)

    # vpn
    def describe_vpn(self, **kwargs):
        req = models.CreateVpnGatewayRequest()
        return self.do_request(self.client.CreateVpnGateway, req, **kwargs)

    # havip
    def describe_havip(self, **kwargs):
        req = models.DescribeHaVipsRequest()
        return self.do_request(self.client.DescribeHaVips, req, **kwargs)


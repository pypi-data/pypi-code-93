from .client import AliCloudClient

from aliyunsdkdds.request.v20151201.CreateDBInstanceRequest import CreateDBInstanceRequest
from aliyunsdkdds.request.v20151201.DeleteDBInstanceRequest import DeleteDBInstanceRequest
from aliyunsdkdds.request.v20151201.DescribeAvailableResourceRequest import DescribeAvailableResourceRequest
from aliyunsdkdds.request.v20151201.AllocatePublicNetworkAddressRequest import AllocatePublicNetworkAddressRequest
from aliyunsdkdds.request.v20151201.ReleasePublicNetworkAddressRequest import ReleasePublicNetworkAddressRequest
from aliyunsdkdds.request.v20151201.DescribeDBInstanceAttributeRequest import DescribeDBInstanceAttributeRequest
from aliyunsdkdds.request.v20151201.DescribeDBInstancesRequest import DescribeDBInstancesRequest
from aliyunsdkdds.request.v20151201.ModifySecurityIpsRequest import ModifySecurityIpsRequest
from aliyunsdkdds.request.v20151201.DescribeSecurityIpsRequest import DescribeSecurityIpsRequest
from aliyunsdkdds.request.v20151201.DescribeShardingNetworkAddressRequest import DescribeShardingNetworkAddressRequest


class DdsClient(AliCloudClient):
    def __init__(self, secret_id, secret_key, region):
        super(DdsClient, self).__init__(secret_id, secret_key, region)

    def create(self, query_params=None, body_params=None):
        return self.do_request(CreateDBInstanceRequest, query_params, body_params)

    def delete(self, query_params=None, body_params=None):
        return self.do_request(DeleteDBInstanceRequest, query_params, body_params)

    def list_DB_instance(self, query_params=None, body_params=None):
        return self.do_request(DescribeDBInstancesRequest, query_params, body_params)

    def get_DB_instance_attribute(self, query_params=None, body_params=None):
        return self.do_request(DescribeDBInstanceAttributeRequest, query_params, body_params)

    def get_available_resource(self, query_params=None, body_params=None):
        return self.do_request(DescribeAvailableResourceRequest, query_params, body_params)

    def get_sharding_network_address(self, query_params=None, body_params=None):
        return self.do_request(DescribeShardingNetworkAddressRequest, query_params, body_params)

    def allocate_public_network_address(self, query_params=None, body_params=None):
        return self.do_request(AllocatePublicNetworkAddressRequest, query_params, body_params)

    def release_public_network_address(self, query_params=None, body_params=None):
        return self.do_request(ReleasePublicNetworkAddressRequest, query_params, body_params)

    def modify_security_ips(self, query_params=None, body_params=None):
        return self.do_request(ModifySecurityIpsRequest, query_params, body_params)

    def get_security_ips(self, query_params=None, body_params=None):
        return self.do_request(DescribeSecurityIpsRequest, query_params, body_params)

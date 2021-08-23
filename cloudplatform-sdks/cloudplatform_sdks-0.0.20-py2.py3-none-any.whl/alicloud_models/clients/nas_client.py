from .client import AliCloudClient

from aliyunsdknas.request.v20170626.CreateFileSystemRequest import CreateFileSystemRequest
from aliyunsdknas.request.v20170626.DeleteFileSystemRequest import DeleteFileSystemRequest
from aliyunsdknas.request.v20170626.DescribeFileSystemsRequest import DescribeFileSystemsRequest
from aliyunsdknas.request.v20170626.CreateMountTargetRequest import CreateMountTargetRequest
from aliyunsdknas.request.v20170626.DescribeMountTargetsRequest import DescribeMountTargetsRequest
from aliyunsdknas.request.v20170626.DeleteMountTargetRequest import DeleteMountTargetRequest
from aliyunsdknas.request.v20170626.CreateLifecyclePolicyRequest import CreateLifecyclePolicyRequest
from aliyunsdknas.request.v20170626.DeleteLifecyclePolicyRequest import DeleteLifecyclePolicyRequest
from aliyunsdknas.request.v20170626.DescribeLifecyclePoliciesRequest import DescribeLifecyclePoliciesRequest
from aliyunsdkcore.acs_exception.exceptions import ServerException


class NasClient(AliCloudClient):
    def __init__(self, secret_id, secret_key, region):
        super(NasClient, self).__init__(secret_id, secret_key, region)

    def create_file_system(self, query_params=None, body_params=None):
        return self.do_request(CreateFileSystemRequest, query_params, body_params)

    def delete_file_system(self, query_params=None, body_params=None):
        return self.do_request(DeleteFileSystemRequest, query_params, body_params)

    def describe_file_systems(self, query_params=None, body_params=None):
        try:
            response = self.do_request(DescribeFileSystemsRequest, query_params, body_params)
            return response
        except ServerException as e:
            if e.get_http_status() == 404:
                return None
            else:
                raise e

    def create_mount_target(self, query_params=None, body_params=None):
        return self.do_request(CreateMountTargetRequest, query_params, body_params)

    def describe_mount_target(self, query_params=None, body_params=None):
        return self.do_request(DescribeMountTargetsRequest, query_params, body_params)

    def delete_mount_target(self, query_params=None, body_params=None):
        return self.do_request(DeleteMountTargetRequest, query_params, body_params)

    def create_lifecycle_policy(self, query_params=None, body_params=None):
        return self.do_request(CreateLifecyclePolicyRequest, query_params, body_params)

    def delete_lifecycle_policy(self, query_params=None, body_params=None):
        return self.do_request(DeleteLifecyclePolicyRequest, query_params, body_params)

    def describe_lifecycle_policies(self, query_params=None, body_params=None):
        return self.do_request(DescribeLifecyclePoliciesRequest, query_params, body_params)
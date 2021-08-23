from .client import TencentClient
from tencentcloud.cfs.v20190719 import cfs_client as tencent_cfs_client, models
from tencentcloud.cfs.v20190719 import models


class CfsClient(TencentClient):
    def __init__(self, *args, **kwargs):
        super(CfsClient, self).__init__(*args, **kwargs)
        self.httpProfile.endpoint = "cfs.tencentcloudapi.com"
        self.clientProfile.httpProfile = self.httpProfile
        self.client = tencent_cfs_client.CfsClient(self.cred, self.region, self.clientProfile)

    def create_cfs_file_system(self, **kwargs):
        req = models.CreateCfsFileSystemRequest()
        return self.do_request(self.client.CreateCfsFileSystem, req, **kwargs)

    def delete_cfs_file_system(self, **kwargs):
        req = models.DeleteCfsFileSystemRequest()
        return self.do_request(self.client.DeleteCfsFileSystem, req, **kwargs)

    def describe_cfs_file_systems(self, **kwargs):
        req = models.DescribeCfsFileSystemsRequest()
        return self.do_request(self.client.DescribeCfsFileSystems, req, **kwargs)

    def describe_mount_targets(self, **kwargs):
        req = models.DescribeMountTargetsRequest()
        return self.do_request(self.client.DescribeMountTargets, req, **kwargs)

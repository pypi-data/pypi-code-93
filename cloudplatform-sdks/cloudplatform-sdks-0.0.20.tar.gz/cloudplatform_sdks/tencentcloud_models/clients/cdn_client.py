from .client import TencentClient
from tencentcloud.cdn.v20180606 import cdn_client as tencent_cdn_client
from tencentcloud.cdn.v20180606 import models


class CdnClient(TencentClient):
    def __init__(self, *args, **kwargs):
        super(CdnClient, self).__init__(*args, **kwargs)
        self.httpProfile.endpoint = "cdn.tencentcloudapi.com"
        self.clientProfile.httpProfile = self.httpProfile
        self.client = tencent_cdn_client.CdnClient(self.cred, self.region, self.clientProfile)

    def refresh_urls_cache(self, **kwargs):
        req = models.PurgeUrlsCacheRequest()
        return self.do_request(self.client.PurgeUrlsCache, req, **kwargs)

    def refresh_path_cache(self, **kwargs):
        req = models.PurgePathCacheRequest()
        return self.do_request(self.client.PurgePathCache, req, **kwargs)

    def push_urls_cache(self, **kwargs):
        req = models.PushUrlsCacheRequest()
        return self.do_request(self.client.PushUrlsCache, req, **kwargs)

    def describe_push_tasks(self, **kwargs):
        req = models.DescribePushTasksRequest()
        return self.do_request(self.client.DescribePushTasks, req, **kwargs)

    def describe_refresh_tasks(self, **kwargs):
        req = models.DescribePurgeTasksRequest()
        return self.do_request(self.client.DescribePurgeTasks, req, **kwargs)

    def list_domains(self, **kwargs):
        req = models.DescribeDomainsRequest()
        return self.do_request(self.client.DescribeDomains, req, **kwargs)

    def stop_cdn_domain(self, **kwargs):
        req = models.StopCdnDomainRequest()
        return self.do_request(self.client.StopCdnDomain, req, **kwargs)

    def start_cdn_domain(self, **kwargs):
        req = models.StartCdnDomainRequest()
        return self.do_request(self.client.StartCdnDomain, req, **kwargs)

    def delete_cdn_domain(self, **kwargs):
        req = models.DeleteCdnDomainRequest()
        return self.do_request(self.client.DeleteCdnDomain, req, **kwargs)



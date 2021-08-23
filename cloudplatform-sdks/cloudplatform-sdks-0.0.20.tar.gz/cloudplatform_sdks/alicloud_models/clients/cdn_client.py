from .client import AliCloudClient
from aliyunsdkcdn.request.v20180510.DescribeUserDomainsRequest import DescribeUserDomainsRequest
from aliyunsdkcdn.request.v20180510.PushObjectCacheRequest import PushObjectCacheRequest
from aliyunsdkcdn.request.v20180510.RefreshObjectCachesRequest import RefreshObjectCachesRequest
from aliyunsdkcdn.request.v20180510.DescribeRefreshTasksRequest import DescribeRefreshTasksRequest
from aliyunsdkcdn.request.v20180510.StartCdnDomainRequest import StartCdnDomainRequest
from aliyunsdkcdn.request.v20180510.StopCdnDomainRequest import StopCdnDomainRequest
from aliyunsdkcdn.request.v20180510.DeleteCdnDomainRequest import DeleteCdnDomainRequest


class CdnClient(AliCloudClient):
    def __init__(self, secret_id, secret_key, region):
        super(CdnClient, self).__init__(secret_id, secret_key, region)

    def describe_user_domains(self, query_params=None, body_params=None):
        return self.do_request(DescribeUserDomainsRequest, query_params, body_params)

    def describe_tasks_state(self, query_params=None):
        return self.do_request(DescribeRefreshTasksRequest, query_params=query_params)

    def push_object_cache(self, query_params=None, body_params=None):
        return self.do_request(PushObjectCacheRequest, query_params, body_params)

    def fresh_object_cache(self, query_params=None, body_params=None):
        return self.do_request(RefreshObjectCachesRequest, query_params, body_params)

    def describe_tasks(self, query_params=None):
        return self.do_request(DescribeRefreshTasksRequest, query_params)['Tasks']['CDNTask']

    def start_cdn_domain(self, query_params=None):
        return self.do_request(StartCdnDomainRequest, query_params)

    def stop_cdn_domain(self, query_params=None):
        return self.do_request(StopCdnDomainRequest, query_params)

    def delete_cdn_domain(self, query_params=None):
        return self.do_request(DeleteCdnDomainRequest, query_params)

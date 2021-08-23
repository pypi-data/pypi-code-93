from .client import TencentClient
from tencentcloud.clb.v20180317 import clb_client as tencent_clb_client
from tencentcloud.clb.v20180317 import models

class ClbClient(TencentClient):
    def __init__(self, *args, **kwargs):
        super(ClbClient, self).__init__(*args, **kwargs)
        self.httpProfile.endpoint = "clb.tencentcloudapi.com"
        self.clientProfile.httpProfile = self.httpProfile
        self.client = tencent_clb_client.ClbClient(self.cred, self.region, self.clientProfile)

    def create_load_balancers(self, **kwargs):
        req = models.CreateLoadBalancerRequest()
        return self.do_request(self.client.CreateLoadBalancer, req, **kwargs).get('LoadBalancerIds')[0]

    def delete_load_balancers(self, **kwargs):
        req = models.DeleteLoadBalancerRequest()
        self.do_request(self.client.DeleteLoadBalancer, req, **kwargs)

    def describe_load_balancers(self, **kwargs):
        req = models.DescribeLoadBalancersRequest()
        return self.do_request(self.client.DescribeLoadBalancers, req, **kwargs)

    def describe_listeners(self, **kwargs):
        req = models.DescribeListenersRequest()
        return self.do_request(self.client.DescribeListeners, req, **kwargs)

    def create_listener(self, **kwargs):
        req = models.CreateListenerRequest()
        return self.do_sync_request(self.client.CreateListener, req, **kwargs).get('ListenerIds')[0]

    def delete_listener(self, **kwargs):
        req = models.DeleteListenerRequest()
        return self.do_request(self.client.DeleteListener, req, **kwargs)

    def add_member(self, **kwargs):
        req = models.RegisterTargetsRequest()
        return self.do_sync_request(self.client.RegisterTargets, req, **kwargs)

    def del_member(self, **kwargs):
        req = models.DeregisterTargetsRequest()
        return self.do_sync_request(self.client.DeregisterTargets, req, **kwargs)

    def describe_members(self, **kwargs):
        req = models.DescribeTargetsRequest()
        return self.do_request(self.client.DescribeTargets, req, **kwargs)

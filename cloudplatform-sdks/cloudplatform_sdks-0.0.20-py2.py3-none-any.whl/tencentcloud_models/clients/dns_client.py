from .client import TencentClient
from tencentcloud.dnspod.v20210323 import dnspod_client as tencent_dns_client
from tencentcloud.dnspod.v20210323 import models


class DnsClient(TencentClient):
    def __init__(self, *args, **kwargs):
        super(DnsClient, self).__init__(*args, **kwargs)
        self.httpProfile.endpoint = "dnspod.tencentcloudapi.com"
        self.clientProfile.httpProfile = self.httpProfile
        self.client = tencent_dns_client.DnspodClient(self.cred, self.region, self.clientProfile)

    def describe_domain_list(self, **kwargs):
        req = models.DescribeDomainListRequest()
        return self.do_request(self.client.DescribeDomainList, req, **kwargs)

    def create_record(self, **kwargs):
        req = models.CreateRecordRequest()
        return self.do_request(self.client.CreateRecord, req, **kwargs)

    def delete_record(self, **kwargs):
        req = models.DeleteRecordRequest()
        return self.do_request(self.client.DeleteRecord, req, **kwargs)

    def modify_record(self, **kwargs):
        req = models.ModifyRecordRequest()
        return self.do_request(self.client.ModifyRecord, req, **kwargs)

    def describe_record(self, **kwargs):
        req = models.DeleteRecordRequest()
        return self.do_request(self.client.DescribeRecord, req, **kwargs)

    def describe_record_list(self, **kwargs):
        req = models.DescribeRecordListRequest()
        return self.do_request(self.client.DescribeRecordList, req, **kwargs)

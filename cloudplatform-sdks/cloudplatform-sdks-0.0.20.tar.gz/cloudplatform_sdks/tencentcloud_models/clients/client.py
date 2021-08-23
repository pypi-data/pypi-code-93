import time
import json
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.clb.v20180317 import models


class TencentClient:
    def __init__(self, secret_id, secret_key, region):
        self.cred = credential.Credential(secret_id, secret_key)
        self.secret_id = secret_id
        self.secret_key = secret_key
        self.region = region
        self.httpProfile = HttpProfile()
        self.clientProfile = ClientProfile()
        self.client = None

    def do_request(self, method, req, **kwargs):
        for key, value in kwargs.items():
            setattr(req, key, value)
        try:
            return json.loads(method(req).to_json_string())
        except TencentCloudSDKException as e:
            raise e

    def do_sync_request(self, method, req, timeout=60, interval=10, **kwargs):
        response = self.do_request(method, req, **kwargs)
        request_id = response.get('RequestId')
        query_request = models.DescribeTaskStatusRequest()
        query_request.TaskId = request_id
        while timeout > 0:
            time.sleep(interval)
            timeout -= interval
            status = self.do_request(self.client.DescribeTaskStatus, query_request).get('Status')
            if status == 0:  # success
                return response
            elif status == 1:  # failed
                raise Exception("Request: {} failed".format(req))
            else:  # progressing
                pass

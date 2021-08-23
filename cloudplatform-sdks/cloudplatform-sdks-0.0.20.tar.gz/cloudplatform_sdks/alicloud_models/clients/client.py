from aliyunsdkcore.client import AcsClient
import json

class AliCloudClient:
    def __init__(self, secret_id, secret_key, region):
        self.secret_id = secret_id
        self.secret_key = secret_key
        self.region = region
        self.client = AcsClient(self.secret_id, self.secret_key, self.region)

    def do_request(self, req_cls, query_params=None, body_params=None):
        req = req_cls()
        if query_params:
            for k, v in query_params.items():
                req.add_query_param(k, v)
        if body_params:
            for k, v in body_params.items():
                req.add_body_params(k, v)
        try:
            res = self.client.do_action_with_exception(req)
        except Exception as e:
            raise e
        return json.loads(res)

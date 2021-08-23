import json
import requests
import base64


class CMPClient:

    def __init__(self, cmp_url, tenant_id):
        self.cmp_url = cmp_url
        self.tenant_id = tenant_id

    def headers(self):
        resp = self.login()
        cookies = resp.cookies.items()
        cookie = ''
        for name, value in cookies:
            cookie += '{0}={1};'.format(name, value)
        return {
            "cookie": cookie,
            "Content-Type": "application/json; charset=utf-8"
        }

    def check_response_code(self, resp):
        if int(resp.status_code) != 200:
            raise Exception(
                "query failed, the error message is {0}, the status code is {1}".format(resp.text, resp.status_code))

    def request_no_header(self, method, url, data={}):
        resp = requests.request(method, url, data=data, verify=False)
        self.check_response_code(resp)
        return resp

    def common_request(self, method, endpoint, data={}, json={}):
        url = self.cmp_url + endpoint
        header = self.headers()
        resp = requests.request(method, url, headers=header, data=data, json=json, verify=False)
        self.check_response_code(resp)
        return resp

    def login(self):
        url = self.cmp_url + "/platform-api/login?tenant={}".format(self.tenant_id)
        data = {
            'secretKey': 'a6ae1360dacc6ee6fa9f43258aaf080129db4e2666deee08f847b80405a5286fc904a97c73c9bc0fcc8cf25a465686a9',
            'userId': 'sysadmin'
        }
        metadata = {
            'accessKey': base64.b64encode(bytes(json.dumps(data), encoding='utf-8'))
        }
        return self.request_no_header("post", url, data=metadata)

    def request_admin_in_secret_key(self):
        resp = self.login()
        cookies = resp.cookies.items()
        cookie = ''
        for name, value in cookies:
            cookie += '{0}={1};'.format(name, value)
        headers = {
            "cookie": cookie,
            "Content-Type": "application/json; charset=utf-8"
        }
        return headers

    def create_integration_mapping(self, kwargs):
        data = {
            "internalId": kwargs.get("internalId"),
            "internalName": kwargs.get("internalName"),
            "internalClass": kwargs.get("internalClass"),
            "integrationId": kwargs.get("integrationId"),
            "integrationName": kwargs.get("integrationName"),
            "exts": kwargs.get("exts"),
            "integrationPlatformId": kwargs.get("integrationPlatformId")
        }
        url = self.cmp_url + "/platform-api/integration/mapping"
        resp = self.common_request("post", url, json=data)
        return resp.content.decode()

    def update_integration_mapping(self, data, mapping_id):
        url = self.cmp_url + "/platform-api/integration/mapping/{}".format(mapping_id)
        return self.common_request("put", url, json=data)

    def delete_integration_mapping(self, mapping_id):
        url = self.cmp_url + "/platform-api/integration/mapping/{}".format(mapping_id)
        return self.common_request("delete", url)

    def query_object_by_intetnal(self, internal_id, cloud_entry_id):
        url = self.cmp_url + "/platform-api/integration/mapping/?internalId={}&integrationPlatformId={}".format(
            internal_id, cloud_entry_id)
        resp = self.common_request("get", url)
        if not resp.content:
            raise Exception("not exist")
        return json.loads(resp.content)

    def query_object_by_integration(self, integration_id, cloud_entry_id):
        url = self.cmp_url + "/platform-api/integration/mapping/?integrationId={}&integrationPlatformId={}".format(
            integration_id, cloud_entry_id)
        resp = self.common_request("get", url)
        return json.loads(resp.content)

    def query_user(self, user_id):
        url = self.cmp_url + "/platform-api/users/{}".format(user_id)
        resp = self.common_request("get", url)
        return json.loads(resp.content)

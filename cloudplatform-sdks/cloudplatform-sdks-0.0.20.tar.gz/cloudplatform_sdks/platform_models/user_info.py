from .clients import CMPClient
import json


class UserInfo(CMPClient):

    def __init__(self, cmp_url, tenant_id):
        super(UserInfo, self).__init__(cmp_url, tenant_id)

    def query_user(self, user_id):
        """
        :param user_id:
        :return: User Object
        """
        url = "/platform-api/users/{}".format(user_id)
        resp = self.common_request("get", url)
        return json.loads(resp.content)
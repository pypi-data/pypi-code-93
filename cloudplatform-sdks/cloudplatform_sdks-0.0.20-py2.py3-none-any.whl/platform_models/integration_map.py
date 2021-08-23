from .clients import CMPClient
import json


class IntegrationMap(CMPClient):

    def __init__(self, cmp_url, tenant_id):
        super(IntegrationMap, self).__init__(cmp_url, tenant_id)

    def create_integration_mapping(self, kwargs):
        """
        :param kwargs:
        :return: mapping Id
        """
        data = {
            "internalId": kwargs.get("internalId"),
            "internalName": kwargs.get("internalName"),
            "internalClass": kwargs.get("internalClass"),
            "integrationId": kwargs.get("integrationId"),
            "integrationName": kwargs.get("integrationName"),
            "exts": kwargs.get("exts"),
            "integrationPlatformId": kwargs.get("integrationPlatformId")
        }
        url = "/platform-api/integration/mapping"
        resp = self.common_request("post", url, json=data)
        return resp.content.decode()

    def update_integration_mapping(self, data, mapping_id):
        """
        :param data:  Map Object
        :param mapping_id:
        :return:
        """
        url = "/platform-api/integration/mapping/{}".format(mapping_id)
        return self.common_request("put", url, json=data)

    def delete_integration_mapping(self, mapping_id):
        url = "/platform-api/integration/mapping/{}".format(mapping_id)
        return self.common_request("delete", url)

    def query_object_by_intetnal(self, internal_id, cloud_entry_id):
        """
        :param internal_id:
        :param cloud_entry_id:
        :return: Map Object
        """
        url = "/platform-api/integration/mapping/?internalId={}&integrationPlatformId={}".format(
            internal_id, cloud_entry_id)
        resp = self.common_request("get", url)
        if not resp.content:
            return
        return json.loads(resp.content)

    def query_object_by_integration(self, integration_id, cloud_entry_id):
        """
        :param integration_id:
        :param cloud_entry_id:
        :return:  Map Object
        """
        url = "/platform-api/integration/mapping/?integrationId={}&integrationPlatformId={}".format(
            integration_id, cloud_entry_id)
        resp = self.common_request("get", url)
        if not resp:
            return
        return json.loads(resp.content)
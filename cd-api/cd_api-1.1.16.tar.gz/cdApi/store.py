'''
@说明    :门店接口。
@时间    :2020/2/13 下午4:28:26
@作者    :任秋锴
@版本    :1.0
'''

from loguru import logger
from .base import base


class store(base):
    def __init__(self, token):
        super().__init__(token)

    def list(self, pageNum=1, pageSize=10):
        api_name = "manager/store/get_sysuser_store_tree"
        data = {
            "pageNum": pageNum,
            "pageSize": pageSize,
        }
        return self.request(api_name, data, method="POST")

    def getCompanyList(self):
        result = self.list()
        for company_info in result.get("data"):
            company_id = company_info.get("id")
            company_name = company_info.get("name")
            company_code = company_info.get("storeCode")
            company_type = company_info.get("type")
            company_parent_id = company_info.get("parentId")
            company_list = company_info.get("list")
            data = {
                "company_id": company_id,
                "company_name": company_name,
                "company_code": company_code,
                "company_type": company_type,
                "company_parent_id": company_parent_id,
            }
            yield data

    def getStoreList(self):
        result = self.list()
        for company_info in result.get("data"):
            company_id = company_info.get("id")
            company_name = company_info.get("name")
            company_code = company_info.get("storeCode")
            company_type = company_info.get("type")
            company_parent_id = company_info.get("parentId")
            company_list = company_info.get("list")
            for store_info in company_list:
                store_id = store_info.get("id")
                store_name = store_info.get("name")
                store_code = store_info.get("storeCode")
                store_type = store_info.get("type")
                store_parent_id = store_info.get("parentId")
                data = {
                    "store_id": store_id,
                    "store_name": store_name,
                    "store_code": store_code,
                    "store_type": store_type,
                    "store_parent_id": store_parent_id,
                }
                yield data

    def create(self, name, specCode):
        api_name = ""
        data = {
            "id": 10270
        }
        return self.request(api_name, data, method="POST")

    def read(self, _id):
        api_name = "manager/store/info"
        data = {
            "id": _id,
        }
        response = self.request(api_name, data, method="GET")
        # print(response)
        return response

    def update(self, data):
        api_name = "manager/store/update"
        response = self.request(api_name, data, method="POST")
        # print(response)
        return self.response(response)

    def updateDemo(self):
        data = {
            'logoUrl': "",
            'storeCode': "",
            'storeType': 0,
            'address': "上海市浦东新区浦东南路2250号",
            'province': "上海市",
            'city': "上海市",
            'area': "浦东新区",
            'longitude': "123.51",
            'latitude': "31.20",
            'level': 2,
            'managerMobile': "",
            'managerName': "",
            'name': "测试店（滨江）",
            'parentId': 10269,
            'type': 0,
            'takeStatus': 0,
            'accountId': None,
            'regionValue': ["上海市", "上海市", "浦东新区"],
        }
        _id = 10270
        self.update(_id, data)

    def updateGPS(self, _id, lat, lng):
        data = self.read(_id)
        data = data.get("data")
        data["longitude"] = lng
        data["latitude"] = lat
        self.update(data)

    def update_manager_mobile(self, _id, manager_mobile):
        data = self.read(_id)
        data = data.get("data")
        data["managerMobile"] = manager_mobile
        self.update(data)

    def delete(self):
        pass

    def code2id(self):
        """
        ### 此方法得到一个code和id对应的大字典来查找对应的值。
        """
        result = {}
        for data in self.getStoreList():
            store_code = data.get("store_code")
            store_id = data.get("store_id")
            company_id = data.get("store_parent_id")
            result[store_code] = {
                "store_id": store_id,
                "company_id": company_id,
            }
        return result

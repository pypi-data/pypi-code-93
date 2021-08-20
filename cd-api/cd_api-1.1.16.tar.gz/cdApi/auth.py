'''
@说明    :权限接口。
@时间    :2020/2/13 下午4:28:26
@作者    :任秋锴
@版本    :1.0
'''

from loguru import logger
from .base import base


class auth(base):
    def __init__(self, token):
        super().__init__(token)

    def list(self, mobile=None, pageNum=1, pageSize=10):
        api_name = "manager/sysuser/list"
        data = {
            "pageNum": pageNum,
            "pageSize": pageSize,
        }
        if mobile:
            data["mobile"] = mobile
        return self.request(api_name, data)

    def role_list(self):
        api_name = "manager/role/rolelist"
        data = {
        }
        return self.request(api_name, data)

    def getAllData(self, pageNum=1, pageSize=10):
        while 1:
            response = self.list(pageNum, pageSize)
            rows = response.get("data")
            rows = rows.get("dataList")
            if len(rows) >= pageSize:
                pageNum += 1
                yield rows
            else:
                yield rows
                return

    def create(self, data):
        """
        数据样式：
        data = {
            "name": "任秋锴", 
            "mobile": "13801587423", 
            "roleIds": [4], 
            "status": 1, # 已关闭员工账号
            "status2": True,# 已关闭员工账号
            "storeType": 2,
            "companyId": 77,
            "companyId2": [], 
            "storeId": 3, 
            "storeId2": [], 
            "storeIds": [77, 3]
            }
        """
        api_name = "manager/sysuser/add"
        return self.request(api_name, data, method="POST")

    def create_store(self, name, mobile, role_ids: list, company_id, store_id):
        """
        # 增加门店账号权限。
        只支持一个分公司，一个门店
        """
        data = {
            "name": name,
            "mobile": mobile,
            "roleIds": role_ids,
            "status": 1,
            "status2": True,
            "storeType": 2,  # 门店权限
            "companyId": company_id,
            "companyId2": [],
            "storeId": store_id,
            "storeId2": [],
            "storeIds": [company_id, store_id]
        }
        return self.create(data)

    def update_store(self, name, mobile, role_ids: list, company_id, store_id, _id):
        """
        # 修改门店账号权限。
        只支持一个分公司，一个门店
        """
        data = {
            "name": name,
            "mobile": mobile,
            "roleIds": role_ids,
            "status": 1,
            "status2": True,
            "storeType": 2,  # 门店权限
            "companyId": company_id,
            "companyId2": [],
            "storeId": store_id,
            "storeId2": [],
            "storeIds": [company_id, store_id],
            "id": _id,
            # "type": None,
            # "corpId": None,
            "isAdmin": 0
        }
        logger.debug(data)
        return self.update(data)

    def read(self, _id):
        api_name = "manager/sysuser/info"
        data = {
            "id": _id,
        }
        response = self.request(api_name, data, method="GET")
        # print(response)
        return response

    def update(self, data):
        api_name = "manager/sysuser/update"
        response = self.request(api_name, data, method="POST")
        return self.response(response)

    def delete(self):
        pass

    def update_status(self, _id, status):
        """
        status:1开启0关闭
        """
        api_name = "manager/sysuser/updatestatus"
        data = {"status": status, "id": _id}
        response = self.request(api_name, data, method="POST")
        return self.response(response)

    def updateUserAuth(self, data):
        return self.update(data)

    def updateUserAuthDemo(self, companyId):
        data = {
            "name": "秋锴1",
            "mobile": "13801587423",
            "roleIds": [36], "status2": True, "storeType": 1,
            "companyId": companyId, "companyId2": [],
            "storeId": "", "storeId2": [], "id": 13160, "storeIds": [companyId],
            "status": 1, "type": None, "corpId": None, "isAdmin": 0
        }
        (self.update(data))

    def get_role_map(self):
        role_map = {}
        for role in self.role_list().get("data"):
            role_id = role.get("id")
            role_name = role.get("name")
            role_map[role_name] = role_id
        return role_map

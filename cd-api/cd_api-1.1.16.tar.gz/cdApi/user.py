'''
@说明    :草动用户接口。
@时间    :2020/2/13 下午4:28:26
@作者    :任秋锴
@版本    :1.0
'''

from typing import List
from .base import base


class user(base):
    def __init__(self, token):
        super().__init__(token)

    def list(self,
             storeIdKey=None, companyId=None, mobile=None,
             pageNum=1, pageSize=10,):
        api_name = "manager/user/listemp"
        data = {
            "pageNum": pageNum,
            "pageSize": pageSize,
            "storeIdKey": storeIdKey,
            "companyId": companyId,
            "mobile": mobile,
        }
        return self.request(api_name, data)

    def batch_update(self, data):
        api_name = "manager/user/batch_update"
        return self.request(api_name, data)

    def batch_delete(self, idList: List, status=0):
        """
        批量离职
        """
        api_name = "manager/user/batch_update"
        data = {
            "idList": idList,
            "status": status,
        }
        return self.request(api_name, data, method="POST")

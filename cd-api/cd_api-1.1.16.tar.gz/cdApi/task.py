'''
@说明    :任务接口。
@时间    :2020/3/19 下午4:51:48
@作者    :任秋锴
@版本    :1.0
'''

from .base import base


class task(base):
    def __init__(self, token):
        super().__init__(token)

    def list(self, pageNum=1, pageSize=10):
        api_name = "manager/task/list"
        data = {
            "pageNum": pageNum,
            "pageSize": pageSize,
        }
        return self.request(api_name, data)

    def create(self, data):
        api_name = "manager/task/add"
        return self.request(api_name, data, method="POST")

    def read(self, _id):
        api_name = "manager/task/info"
        data = {
            "id": _id,
        }
        response = self.request(api_name, data, method="GET")
        return self.response(response)

    def update(self, data):
        api_name = "manager/task/update"
        response = self.request(api_name, data, method="POST")
        return self.response(response)

    def delete(self):
        pass

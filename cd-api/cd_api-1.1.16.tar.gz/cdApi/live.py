'''
@说明    :直播接口。
@时间    :2020/3/19 下午4:51:48
@作者    :任秋锴
@版本    :1.0
'''

from .base import base


class live(base):
    def __init__(self, token):
        super().__init__(token)

    def list(self, pageNum=1, pageSize=10):
        api_name = "manager/live_room/list"
        data = {
            "pageNum": pageNum,
            "pageSize": pageSize,
        }
        return self.request(api_name, data)

    def sync(self, data):
        api_name = "manager/live_room/sync"
        return self.request(api_name, data, method="POST")

    def read(self, _id):
        api_name = "manager/live_room/info"
        data = {
            "LiveRoomId": _id,
        }
        response = self.request(api_name, data, method="GET")
        return response

    def update(self, data):
        api_name = "manager/live_room/update"
        response = self.request(api_name, data, method="POST")
        return self.response(response)

    def updateDemo(self):
        # 直播室可见门店编辑
        data = {
            "id": 230,
            "storeList": [
                {"id": 1290, "type": 0, "parentId": 1289}
            ],
        }
        return self.update(data)

    def delete(self):
        api_name = "manager/live_room/delete"
        response = self.request(api_name, method="GET")
        return self.response(response)

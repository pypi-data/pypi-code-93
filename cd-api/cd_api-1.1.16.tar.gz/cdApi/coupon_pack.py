'''
@Author: Rqk
@Date: 2020-04-26 15:03:56
@LastEditTime: 2020-04-26 15:11:04
@LastEditors: Please set LastEditors
@Description: 优惠券券包接口
'''

from .base import base


class couponPack(base):
    def __init__(self, token):
        super().__init__(token)

    def list(self, pageNum=1, pageSize=10):
        api_name = "manager/coupon_pack/list"
        data = {
            "pageNum": pageNum,
            "pageSize": pageSize,
        }
        return self.request(api_name, data)

    def read(self, _id):
        api_name = "manager/coupon_pack/info"
        data = {
            "id": _id,
        }
        response = self.request(api_name, data, method="GET")
        return self.response(response)

    def update(self, data):
        api_name = "manager/coupon_pack/update"
        response = self.request(api_name, data, method="POST")
        return self.response(response)

    def delete(self):
        pass

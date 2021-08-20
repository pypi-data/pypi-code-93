'''
@说明    :优惠券接口。
@时间    :2020/3/19 下午4:51:48
@作者    :任秋锴
@版本    :1.0
'''


from .base import base


class coupon(base):
    def __init__(self, token):
        super().__init__(token)

    def list(self,
             couponType=None, distType=None,
             storeId=None, companyId=None,
             name=None, type=0,
             pageNum=1, pageSize=10):
        """
        - couponType:优惠券类型 1/3/4/5
        - distType:发放方式 1/2/3/4
        - name:优惠券名称
        - type:优惠券状态，全部0/未开始1/进行中2/已结束3/
        """
        api_name = "manager/coupon/list"
        data = {
            "pageNum": pageNum,
            "pageSize": pageSize,
        }
        return self.request(api_name, data)

    def create(self, data):
        api_name = "manager/coupon/add"
        return self.request(api_name, data, method="POST")

    def read(self, _id):
        api_name = "manager/coupon/info"
        data = {
            "id": _id,
        }
        response = self.request(api_name, data, method="GET")
        return self.response(response)

    def update(self, data):
        api_name = "manager/coupon/edit"
        response = self.request(api_name, data, method="POST")
        return self.response(response)

    def updateDemo(self):
        data = {
            "id": 230,
            "storeList": [
                {"id": 1290, "type": 0, "parentId": 1289}
            ],
        }
        return self.update(data)

    def update_product_list(self, _id, product_id_list: list = []):
        """更新优惠券商品列表

        Args:
            _id (int): 优惠券ID
            product_list (list, optional): 商品列表，支持商品编码，列表保存. Defaults to [].

        Returns:
            response: 返回是否成功标志
        """
        data = self.read(_id)
        data["productId"] = product_id_list
        return self.update(data)

    def delete(self, _id):
        api_name = "manager/coupon/discard"
        data = {"id": _id}
        response = self.request(api_name, data, method="POST")
        return self.response(response)

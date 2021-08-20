"""
@Author: Rqk
@Date: 2020-04-30 14:08:52
@Description: 
@说明    :商品接口。
@时间    :2020/2/13 下午4:28:26
@作者    :任秋锴
@版本    :1.0
"""

from .base import base
from loguru import logger


class storeProduct(base):
    def __init__(self, token):
        super().__init__(token)

    def list(
        self,
        productCode=None,
        companyId=None,
        specCode=None,
        name=None,
        storeStatus=None,
        categoryIds=None,
        pageNum=1,
        pageSize=10,
    ):
        api_name = "manager/storeproduct/list"
        data = {
            "productCode": productCode,
            "companyId": companyId,
            "specCode": specCode,
            "name": name,
            "storeStatus": storeStatus,
            "categoryIds": categoryIds,
            "pageNum": pageNum,
            "pageSize": pageSize,
        }
        result = self.request(api_name, data, method="GET")
        status = result.get("status")
        if status == 200:
            return result.get("data").get("dataList")
        else:
            print(result)

    def create(self, data):
        api_name = "manager/storeproduct/add"
        return self.request(api_name, data, method="POST")

    def read(self, _id):
        url = "manager/storeproduct/info"
        data = {"id": _id}
        return self.request(url, data)

    def update(self, data):
        url = "manager/storeproduct/edit"
        return self.request(url, data, method="POST")

    def delete(self):
        pass

    def updatebatchproduct(self, _id, price):
        api_name = "manager/storeproduct/updatebatchproduct"
        data = {"pidList": [_id], "price": price}
        return self.request(api_name, data, method="POST")

    def update_price(self, store_product_id, price, spec_code=None):
        data = self.read(store_product_id)
        data = data.get("data")
        if data:
            if spec_code:
                # 给了规格码
                for d in data["specificationList"]:
                    if d["specCode"] == spec_code:
                        d["price"] = price
            else:
                # 都没给，全部修改
                for d in data["specificationList"]:
                    d["price"] = price
        return self.update(data)

    def update_price_by_spec_code_list(self, store_product_id, spec_code_list=[]):
        """修改商品价格

        Args:
            store_product_id ([type]): [description]
            spec_code_list (list, optional): [description]. Defaults to [{
                "spec_code":spec_code,
                "price":price,
            }].

        Returns:
            [type]: [description]
        """
        data = self.read(store_product_id)
        data = data.get("data")
        if data:
            for row in spec_code_list:
                spec_code = row.get("spec_code")
                price = row.get("price")
                for d in data["specificationList"]:
                    if d["specCode"] == spec_code:
                        d["price"] = price
            return self.update(data)
        else:
            msg = {
                "store_product_id": store_product_id,
                "msg": "查找不到此商品",
            }
            logger.error(msg)

    def update_inventory(self, store_product_id, spec_inventory):
        """
        spec_inventory = {spec_code:inventory}
        """
        data = self.read(store_product_id)
        data = data.get("data")
        if data:
            update_flag = False
            for d in data["specificationList"]:
                inventory = spec_inventory.get(d["specCode"])
                if inventory:
                    if d["inventory"] != inventory:
                        update_flag = True
                        spec_inventory[f"{d['specCode']}_raw"] = d["inventory"]
                        d["inventory"] = inventory
            if update_flag:
                logger.debug(spec_inventory)
                return self.update(data)
            else:
                logger.success({"msg": "不需要更新库存", "store_product_id": store_product_id})
        else:
            logger.error({"msg": "更新商品库存失败", "store_product_id": store_product_id})

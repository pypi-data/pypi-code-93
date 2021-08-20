'''
@说明    :满减送接口。
@时间    :2020/2/13 下午4:28:26
@作者    :任秋锴
@版本    :1.0
'''

from .base import base
from .product import product
from .store import store


class discount(base):
    def __init__(self, token):
        super().__init__(token)

    def list(self,
             state=None,
             name=None,
             productCodes=None,
             companyId=None,
             storeId=None,
             pageNum=1, pageSize=1000):
        api_name = "manager/discount/list"
        data = {
            "pageNum": pageNum,
            "pageSize": pageSize,
        }
        if state:
            data["state"] = state
        if state:
            data["name"] = name
        if state:
            data["productCodes"] = productCodes
        if state:
            data["companyId"] = companyId
        if state:
            data["storeId"] = storeId
        return self.request(api_name, data)

    def create(self, data):
        api_name = "manager/discount/add"
        response = self.request(api_name, data, method="POST")
        return response

    def createykj(self, storeCodes, productCodes,
                  price, beginTime, endTime, name):
        ''' 一口价导入方案 '''
        beginTime = f"{beginTime} 00:00:00"
        endTime = f"{endTime} 23:59:59"

        # 请求的主数据结构
        data = {
            "activeGoods": 2,
            "beginTime": beginTime,
            "endTime": endTime,
            "expressFree": 1,
            "id": "",
            "name": name,
            "discountType": 2,
            "type": 4,
            "unit": 2,
            "time": [beginTime, endTime],
            "productList": [],
            "rules": [],
            "storeList": [],
        }
        # 添加活动规则
        rule = {
            "id": "",
            "usePrice": 1,
            "price": price,
            "discount": None,
            "giftId": None,
            "giftIds": [],
            "giftRule": 1,
            "giftLimit": None,
        }
        data["rules"].append(rule)
        # 添加门店列表
        s = store(self.token)
        store_map = {}
        for store_data in s.getStoreList():
            store_id = store_data.get("store_id")
            store_code = store_data.get("store_code")
            store_parent_id = store_data.get("store_parent_id")
            store_map[store_code] = [store_id, store_parent_id]
        for store_code in storeCodes:
            store_id, parentId = store_map[store_code]
            data["storeList"].append(
                {"id": store_id, "type": 0, "parentId": parentId})
        # 添加商品列表
        p = product(self.token)
        for code in productCodes:
            product_data = p.list(productCode=code)
            if not product_data:
                print(f"{code}\t商品查找不到。")
                return None
            product_data = product_data[0]
            productId = product_data.get("id")
            product_request_payload = {
                "productId": productId,
                "specType": 1,
                "specIds": [],
                "price": None,
                "beginTime": None,
                "endTime": None,
            }
            data["productList"].append(product_request_payload)
        response = self.create(data)
        print(productCodes, response)
        return response

    def createmz(self, storeCodes, productCodes,
                 rules, beginTime, endTime, name):
        ''' 满折导入方案 '''
        beginTime = f"{beginTime} 00:00:00"
        endTime = f"{endTime} 23:59:59"

        # 请求的主数据结构
        data = {
            "activeGoods": 2,
            "beginTime": beginTime,
            "endTime": endTime,
            "expressFree": 1,
            "id": "",
            "name": name,
            "discountType": 2,
            "type": 2,
            "unit": 2,
            "time": [beginTime, endTime],
            "productList": [],
            "rules": [],
            "storeList": [],
        }
        # 添加活动规则
        for row in rules:
            usePrice, discount_num = row
            rule = {
                "id": "",
                "usePrice": usePrice,
                "price": None,
                "discount": discount_num,
                "giftId": None,
                "giftIds": [],
                "giftRule": 1,
                "giftLimit": None,
            }
            data["rules"].append(rule)
        # 添加门店列表
        data["storeList"] = storeCodes
        # 添加商品列表
        p = product(self.token)
        for code in productCodes:
            product_data = p.list(productCode=code)
            if not product_data:
                print(f"{code}\t商品查找不到。")
                return None
            product_data = product_data[0]
            productId = product_data.get("id")
            product_request_payload = {
                "productId": productId,
                "specType": 1,
                "specIds": [],
                "price": None,
                "beginTime": None,
                "endTime": None,
            }
            data["productList"].append(product_request_payload)
        # print(data)
        response = self.create(data)
        print(productCodes, name, rules, response)
        return response

    def create_example(self):
        api_name = "manager/discount/add"
        data = {
            # 添加门店列表
            # 类型 0门店 1分公司
            "storeList": [
                {"id": 3, "type": 1, "parentId": 0},
                {"id": 11, "type": 0, "parentId": 3},
                {"id": 26, "type": 0, "parentId": 3},
                {"id": 29, "type": 0, "parentId": 3},
                {"id": 27002, "type": 0, "parentId": 3}
            ],
            # 活动商品 1全店 2指定商品
            "activeGoods": 2,
            # 开始结束时间
            "beginTime": "2020-02-15 00:00:00",
            "endTime": "2020-02-22 23:59:59",
            # 是否包邮 0：否 1：是
            "expressFree": 1,
            "id": "",
            # 活动名称
            "name": "整单-一般打折",
            # 商品列表
            # 规格信息
            "productList": [
                {"productId": 15641, "specIds": [], "specType":1}
            ],
            # 折扣类型 1订单优惠 2商品优惠
            "discountType": 2,
            # 类型 1减现金 2打折 3送赠品 4一口价  5第N件打折
            "type": 2,
            # 单位 1元 2件
            "unit": 2,
            # 优惠折扣规则
            "rules": [
                {
                    # 限领限制
                    "giftLimit": "",
                    # 领取规则 1件 2元
                    "giftRule": 1,
                    # 规则id
                    "id": "",
                    # 打折
                    "discount": 9,
                    "isOpenGift": False,
                    # 赠品id
                    "giftIds": [],
                    # 减现金
                    "price":"",
                    # 优惠门槛
                    "usePrice":"0"
                }
            ],
            "time": ["2020-02-15 00:00:00", "2020-02-22 23:59:59"]
        }
        return self.request(api_name, data, method="POST")

    def read(self, _id):
        api_name = f"manager/discount/info"
        data = {
            "discountId": _id,
        }
        response = self.request(api_name, data)
        # print(response)
        return response

    def update(self, data):
        api_name = f"manager/discount/update"
        # print(data)
        response = self.request(api_name, data, method="POST")
        return response

    def copy(self, _id, name=None, beginTime=None, endTime=None):
        response = self.read(_id)
        data = response.get("data")
        rules = data.get("rules")
        data["id"] = ""
        if name:
            data["name"] = name
        if beginTime:
            data["beginTime"] = beginTime
        if endTime:
            data["endTime"] = endTime
        if rules:
            for idx, rule in enumerate(data["rules"]):
                data["rules"][idx]["id"] = ""
        response = self.create(data)
        # print(data, response)
        return response

    def delete(self, _id):
        api_name = f"manager/discount/delete_stop"
        data = {
            "id": _id,
            "operate": 0
        }
        response = self.request(api_name, data, method="POST")
        # print(response)
        return response

'''
@说明    :商品素材接口。
@时间    :2020/2/13 下午4:28:26
@作者    :任秋锴
@版本    :1.0
'''


from .base import base


class material(base):
    def __init__(self, token):
        super().__init__(token)

    def create(self, imgName, imgUrl):
        api_name = "manager/product/material/add"
        data = {
            "materialBatchDTOList": [
                {
                    "labelId": "",
                    "imgName": imgName,
                    "imgUrl": imgUrl,
                    "type": 1,
                    "tag": "",
                }
            ]
        }
        # print(data)
        result = self.request(api_name, data, method="POST")
        status = result.get("status")
        if status == 200:
            return result

    def delete(self, _id):
        api_name = "manager/product/material/delete"
        data = {
            "id": _id
        }
        result = self.request(api_name, data, method="DELETE")
        status = result.get("status")
        if status == 200:
            return result
        else:
            print(result)

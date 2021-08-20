'''
@说明    :订单接口。
@时间    :2020/3/19 下午4:51:48
@作者    :任秋锴
@版本    :1.0
'''

from .base import base
import time
from loguru import logger


class logistics(base):
    def __init__(self, token):
        super().__init__(token)

    def read(self,
             tid,
             order_type=1,
             return_order_sn=None,
             express_package_id=None,
             ):
            #  order_type：类型：1 订单 2换货
            #  return_order_sn 退款单号（T开头的退款单号）
            #  express_package_id 快递包裹ID
        data = {
            "method": "cd.logistics.info.get",
            "time": self.time,
            "tid": tid,
            "order_type": order_type,
        }
        if return_order_sn:
            data["return_order_sn"] = return_order_sn
        if express_package_id:
            data["express_package_id"] = express_package_id
        # logger.debug(data)
        return self.request(method="POST", json=data)

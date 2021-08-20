"""
九牧王接口
https://opendoc.icaodong.com/2019/10/30/adapter-joene/#No-2-1-%E4%BC%9A%E5%91%98%E8%AF%A6%E6%83%85%E6%8E%A5%E5%8F%A3
"""

from .base import base
import time
from loguru import logger


class customer(base):
    def __init__(self, token):
        super().__init__(token)

    def read(self,
             member_phone: str = None,
             wechat_open_id: str = None,
             wechat_union_id: str = None,
             ):
        """会员详情接口

        Args:
            member_phone (str, optional): [会员手机号]. Defaults to None.
            wechat_open_id (str, optional): [微信open_id]. Defaults to None.
            wechat_union_id (str, optional): [微信union_id]. Defaults to None.
        """
        data = {
            "method": "joene.items.member.info.get",
            "time": self.time,
        }
        if member_phone:
            data["member_phone"] = member_phone
        if wechat_open_id:
            data["wechat_open_id"] = wechat_open_id
        if wechat_union_id:
            data["wechat_union_id"] = wechat_union_id
        logger.debug(data)
        return self.request(method="POST", json=data)

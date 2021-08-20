# coding=utf-8
from gyerpsdkcore.client.base import BaseGyErpSdk
from gyerpsdkcore import api


class GyErpSdk(BaseGyErpSdk):
    # 管易云，接口类

    item = api.Item()
    trade = api.Trade()

    def __init__(self, appKey=None, sessionKey=None, secretKey=None):
        super(GyErpSdk, self).__init__(appKey, sessionKey, secretKey)


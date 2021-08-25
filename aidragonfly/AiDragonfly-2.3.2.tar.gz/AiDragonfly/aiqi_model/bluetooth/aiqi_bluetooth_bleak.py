# -*- coding: utf-8 -*-
# @Time    : 2021/8/9 10:23
# @Version : V1.0.0
# @Author  : liumingming
# @FileName: aiqi_bluetooth.py
# @Version : V1.0.0
# @Company ：http://www.iqi-inc.com/
import asyncio

from bleak import BleakClient
from bleak import BleakScanner


class Aiqi_Bluetooth_bleak_Class(BleakClient):
     async def __aexit__(self, exc_type, exc_val, exc_tb):
         pass
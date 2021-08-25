# -*- coding: utf-8 -*-
# @Time    : 2021/8/9 10:23
# @Version : V1.0.0
# @Author  : liumingming
# @FileName: aiqi_bluetooth.py
# @Version : V1.0.0
# @Company ：http://www.iqi-inc.com/
import asyncio
import time

from bleak import BleakClient
from bleak import BleakScanner

from AiDragonfly.aiqi_model.bluetooth.aiqi_bluetooth_bleak import Aiqi_Bluetooth_bleak_Class
from AiDragonfly.common.onebot_common_function import Aiqi_Print_HEX
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData
from AiDragonfly.aiqi_model.bluetooth.aiqi_bluetooth_uuid import aiqi_bluetooth_uuid_class as aiqi_uuid


class Aiqi_Bluetooth_Class:
    client_log = False
    scan_log = False
    bluetooth_client = None
    bluetooth_scaner = None
    connect_stats = False
    __user_scaner_callback = None
    __user_disconnect_callback = None
    __user_recive_callback = None
    __send_err_cnt = 0
    __log_title = 'aiqi blue driver '
    __user_scan_list = []

    def __init__(self, clientlog=False,scanlog=False):
        self.client_log = clientlog
        self.scan_log = scanlog
        self.bluetooth_scaner = BleakScanner()
        self.bluetooth_client = None
        self.bluetooth_scaner.register_detection_callback(self._scan_callback)

    def _scan_callback(self,device: BLEDevice, advertisement_data: AdvertisementData):
        if self.scan_log:
            if device.name != '' and device.name is not None:
                if len(self.__user_scan_list) != 0:
                    for item in self.__user_scan_list:
                        if item.address == device.address:
                            return
                self.__user_scan_list.append(device)
                print(self.__log_title+' scancallback '+device.name + ' ' + device.address, "RSSI:", device.rssi)
        if self.__user_scaner_callback is not None:
            self.__user_scaner_callback(device,advertisement_data)


    def set_scan_callback_regiser(self, callback):
        self.__user_scaner_callback = callback

    def set_disconnect_callback_register(self, callback):
        self.__user_disconnect_callback = callback
    def set_receive_callback_register(self, callback):
        self.__user_recive_callback = callback

    @property
    def Get_User_Scan_List(self):
        return self.__user_scan_list

    def scan_devices_operation(self,devices, namelist=[], maclist=[]):
        newdevs = []
        if len(namelist) == 0 and len(maclist) == 0:
            return devices
        if len(maclist) == 0:
            for dev in devices:
                if dev.name in namelist:
                    # print('has1 :' + dev.name)
                    newdevs.append(dev)
        else:
            for dev in devices:
                if dev.address in maclist:
                    # print('has2 :' + dev.name+' mac:'+dev.address)
                    newdevs.append(dev)
        return newdevs

    async def scan_ctrl(self, ctrl):
        if ctrl:
            self.__user_scan_list = []
            await self.bluetooth_scaner.start()
        else:
            await self.bluetooth_scaner.stop()

    async def connect(self, mac, timeout=8):
        async with Aiqi_Bluetooth_bleak_Class(mac, timeout=timeout) as client:
            def _disconnect_callback(res):
                if self.__user_disconnect_callback is not None:
                    self.__user_disconnect_callback(res)

            def _client_recive_callback(len, data):
                if self.client_log:
                    Aiqi_Print_HEX(data, self.__log_title + ' rev:')
                if self.__user_recive_callback is not None:
                    self.__user_recive_callback(len, data)
            await asyncio.sleep(0.1)
            # client.stop_notify()
            # client.disconnect()
            if self.client_log:
                print(self.__log_title + ' connect ok')
            self.connect_stats = True
            self.bluetooth_client = client
            client.set_disconnected_callback(_disconnect_callback)
            await client.start_notify(aiqi_uuid.Aiqi_Bluetooth_Tx_Char_Uuid, _client_recive_callback)
            return client
    async def senddata(self,data):
        try:
            await self.bluetooth_client.write_gatt_char(aiqi_uuid.Aiqi_Bluetooth_Rx_Char_Uuid, data)
            await asyncio.sleep(0.1)
            self.__send_err_cnt = 0
        except:
            print(self.__log_title + 'send err')
            self.connect_stats = False
            await self.bluetooth_client.disconnect()
    async def disconnect(self):
        if self.bluetooth_client is not None:
            self.bluetooth_client.set_disconnected_callback(None)
            await self.bluetooth_client.disconnect()
            await asyncio.sleep(0.1)
            self.bluetooth_client = None


# -*- coding: utf-8 -*-
# @Time    : 2021/8/7 18:15
# @Author  : liumingming
# @FileName: aiqi_bluetooth_uuid.py
# @Company ：http://www.iqi-inc.com/


xor_index = 18

def _data_xor_check(data):  # 异或校验函数 主要用于报文的校验
    value = 0x00
    for i in data:
        value = value ^ i
    return value



class BlueReport:

    create_connect = bytearray([0x57, 0x01, 0x02, 0xAA])

    def __init__(self):
        self._onebotcc_register_start = bytearray([0x55, 0x01, 0x03, 0x00, 0x01, 0x05, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                 0x00, 0x00, 0xAA])
        self._onebotcc_register_stop = bytearray(
            [0x55, 0x01, 0x03, 0x01, 0x01, 0x05, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
             0x00, 0x00, 0xAA])

    @property
    def onebotcc_register_start(self):
        self._onebotcc_register_start[xor_index] = 0
        self._onebotcc_register_start[xor_index]=_data_xor_check(self._onebotcc_register_start[0:-1])
        return self._onebotcc_register_start

    @property
    def onebotcc_register_stop(self):
        self._onebotcc_register_stop[xor_index] = 0
        self._onebotcc_register_stop[xor_index] = _data_xor_check(self._onebotcc_register_stop[0:-1])
        return self._onebotcc_register_stop






bluereport = BlueReport()




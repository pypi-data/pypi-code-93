# -*- coding: utf-8 -*-
# @Time    : 2021/8/7 18:15
# @Author  : liumingming
# @FileName: aiqi_bluetooth_uuid.py
# @Company ：http://www.iqi-inc.com/


from AiDragonfly.common.onebot_common_function import onebot_xor_check

class _mesh_login_class:
    dev_sn = None
    dev_random = 0
    dev_login_stats = False
    dev_version = 0
    need_login_version = 0x040000

    def Get_Sn_Xor(self):
        pass

    def Get_Version_Str(self):
        return str(self.dev_version >> 24) + '.' + str((self.dev_version >> 16) & 0xff) + '.' + str(
            (self.dev_version >> 8) & 0xff) + '.' + str(self.dev_version & 0xff)

    def Clear(self):
        self.dev_sn = None
        self.dev_random = 0
        self.dev_login_stats = False
        self.dev_version = None

class MeshReport:
    mesh_sn = []
    mesh_sn_xor = 0
    mesh_random = 0

    get_version = bytearray([0x01, 0x54, 0x00])
    get_sn = bytearray([0x00, 0x56])
    get_random = bytearray([0x00, 0x52])


    def __init__(self):
        self._login_in = bytearray([1,0x46,0,0])

    @property
    def login_in(self):
        # self._login_in = bytearray([0x01, 0x46,self.mesh_sn_xor, self.mesh_random])
        self.mesh_sn_xor = onebot_xor_check(self.mesh_sn)
        self._login_in[0] = 0x01
        self._login_in[1] = 0x46
        self._login_in[2] = self.mesh_sn_xor
        self._login_in[3] = self.mesh_random
        return self._login_in


mesh_report = MeshReport()

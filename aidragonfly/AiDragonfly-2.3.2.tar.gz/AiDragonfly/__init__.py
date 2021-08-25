# -*- coding: utf-8 -*-
# @Time    : 2021/8/9 9:04
# @Author  : liumingming
# @FileName: __init__.py.py
# @Company ：http://www.iqi-inc.com/

import platform
import sys

from AiDragonfly.aiqi_main import start
from AiDragonfly.aiqi_main import Aiqi_Bluetooth_Disconnect_CallBack_Register

import AiDragonfly.aiqi_bluetooth_device_type as scan_blue
import AiDragonfly.aiqi_model as model


__run_system = platform.system()

if __run_system == "Darwin":
    pass
elif __run_system == "Windows":
    platform.release()
    if platform.release() == '10':
        pass
        win_ver = platform.version()
        win_verlist = win_ver.split('.')
        __ver_h = win_verlist[0]
        __ver_M = win_verlist[1]
        __ver_L = win_verlist[2]
        print(__run_system + " " + platform.release() + ' ' + platform.version())
    else:
        print(__run_system+" "+platform.release()+' '+platform.version())
        print('系统不支持')
        sys.exit('系统不支持')
    pass
else:
    print('系统不支持')
    sys.exit('系统不支持')


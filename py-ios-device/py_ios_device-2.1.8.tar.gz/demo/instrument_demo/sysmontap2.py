"""
获取系统相关信息，类似 Android TOP，包含进程信息，需要 iOS > 11
"""
import os
import sys
sys.path.append(os.getcwd())

from ios_device.servers.Instrument import InstrumentServer

import json
import time
from ios_device.util import logging

log = logging.getLogger(__name__)


def sysmontap(rpc):

    def dropped_message(res):
        print("[DROP]", res.selector)


    # print(rpc.lockdown.device_id)
    rpc.register_undefined_callback(dropped_message)
    print(rpc.call('com.apple.instruments.server.services.gpu','requestDeviceGPUInfo').selector)
    rpc.call("com.apple.instruments.server.services.gpu", "configureCounters:counterProfile:interval:windowLimit"
                                                          ":tracingPID:",[574],574,1,1,1)


    rpc.stop()


if __name__ == '__main__':
    # rpc = InstrumentServer()
    # addresses, port, psk = rpc.start_wireless()
    # print('start wireless', addresses, port, psk)
    # rpc = rpc.init_wireless(addresses, port, psk)
    rpc = InstrumentServer().init()
    sysmontap(rpc)
    rpc.stop()

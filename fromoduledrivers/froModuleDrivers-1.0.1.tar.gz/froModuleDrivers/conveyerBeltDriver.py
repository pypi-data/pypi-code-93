# -*- encoding=utf-8 -*-

from .baseDriver import BaseDriver
from .protocolHandler import *
from . import LOGGER
import time

tarVersion = "V20210823"

VersionDetail = "当前版本:" + tarVersion + """
---------------------------版本更新信息----------------------------

V20210823:
1.使用新的框架来实现旧的api
------------------------------------------------------------------
"""


class ConveyerBeltDriver(BaseDriver):
    def __init__(self, host="localhost", port=4001):
        super().__init__(host, port)
        self.addProtocol(K12ProtocolHandler())
        self.status = {}

    # 此处result为按协议定义的字段解析过的dict
    # 可根据具体设备进行自定义 状态信息维护、状态查询结果返回等操作。
    # 根据不同的协议返回，包装返回值，使其包含"orderName", 并被查询指令接收。
    def doHandleResult(self, result):
        if result is None or result.get("data") is None:
            if result is not None:
                LOGGER.logger.warning("不能解析的协议:%s" % result)
            return None, False
        else:
            LOGGER.logger.debug("doHandleResult:%s" % result)
            return result, True

    # 查询指令样本，需要等待返回状态值
    def queryOrder(self, *args):
        argList = list(args)
        timeout = argList.pop(0)
        orderName = argList.pop(0)
        data = self.parseOrder(orderName, *argList)
        if data is None:
            return
        self.connector.waitResponse(self.getClientId(), orderName)
        self.connector.sendData(self.getClientId(), data, prior=False)
        time.sleep(timeout)
        return self.connector.getResponse(self.getClientId(), orderName)

    # 不等待返回值，比如上位机软件更新内部设备状态信息
    def excuteOrderRightAway(self, *args):
        argList = list(args)
        orderName = argList.pop(0)
        data = self.parseOrder(orderName, *argList)
        if data is None:
            return
        self.connector.sendData(self.getClientId(), data, prior=False)

    def getVersion(self):
        return tarVersion

    def showVersion(self):
        print(VersionDetail)

    ########################## 以下是传送带控制方法 ############################
    def checkConveyerBeltStatus(self):
        recv_buf = self.queryOrder(1, "03号查询指令", int(255), 0x0101, 0x01, 0)
        if recv_buf is not None:
            return (recv_buf["data"]["数据"] & 0xFF)
        else:
            return False

    def checkConveyerBeltInfr(self):
        recv_buf = self.queryOrder(1, "03号查询指令", int(255), 0x0102, 0x02, 0)
        if recv_buf is not None:
            return [((recv_buf["data"]["数据"] >> 16) & 0xFF),
                    (recv_buf["data"]["数据"] & 0xFF)]
        else:
            return False

        # return self.queryOrder(1, "03号查询指令", 0xFF, 0x0102, 0x02, 0)

    def checkConveyerBeltInfrFront(self):
        recv_buf = self.checkConveyerBeltInfr()
        if recv_buf is not False:
            return recv_buf[0]
        else:
            return False
        # return ((self.queryOrder(1, "03号查询指令", 0xFF, 0x0102, 0x02, 0)) >> 16)

    def checkConveyerBeltInfrBack(self):
        recv_buf = self.checkConveyerBeltInfr()
        if recv_buf is not False:
            return recv_buf[1]
        else:
            return False
        # return ((self.queryOrder(1, "03号查询指令", 0xFF, 0x0102, 0x02, 0)) & 0xFF)

    def startConveyerBelt(self):
        self.excuteOrderRightAway("10号写指令", 0xFF, 0x0101, 0x01, 0x02, 0x0001,
                                  0)

    def backConveyerBelt(self):
        self.excuteOrderRightAway("10号写指令", 0xFF, 0x0101, 0x01, 0x02, 0x0002,
                                  0)

    def stopConveyerBelt(self):
        self.excuteOrderRightAway("10号写指令", 0xFF, 0x0101, 0x01, 0x02, 0x0000,
                                  0)

    def controlConveyerBelt(self, direction=0):
        if direction > 0:
            self.startConveyerBelt()
        elif direction < 0:
            self.backConveyerBelt()
        else:
            self.stopConveyerBelt()

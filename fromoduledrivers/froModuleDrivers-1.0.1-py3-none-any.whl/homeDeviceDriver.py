# -*- encoding=utf-8 -*-

from .baseDriver import BaseDriver
from .protocolHandler import *
from . import LOGGER
import time

tarVersion = "V20210821"

VersionDetail = "当前版本:" + tarVersion + """
---------------------------版本更新信息----------------------------

V20210821:
1.使用新的框架来实现旧的api
------------------------------------------------------------------
"""


class HomeDeviceDict():
    last_speech = 0xFF


class HomeDeviceDriver(BaseDriver, HomeDeviceDict):
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

    # 单参数状态获取返回为true or false
    def isSingleStatusTrueOrFalse(self, moduleID=None, moduleAddr=0):
        recv_buf = self.queryOrder(1, "03号查询指令", int(moduleID), moduleAddr,
                                   0x01, 0)
        if recv_buf is not None:
            if recv_buf["data"]["数据"] == 1:
                return True
            else:
                return False
        else:
            return False

    def getVersion(self):
        return tarVersion

    def showVersion(self):
        print(VersionDetail)

    ########################## 以下是设备控制器控制方法 ############################

    # 灯光
    def openLight(self, moduleID=4):
        self.excuteOrderRightAway("10号写指令", int(moduleID), 0x00AA, 0x01, 0x02,
                                  1, 0)

    def closeLight(self, moduleID=4):
        self.excuteOrderRightAway("10号写指令", int(moduleID), 0x00AA, 0x01, 0x02,
                                  0, 0)

    # 门禁
    def closeDoor(self, moduleID=2):
        self.excuteOrderRightAway("10号写指令", int(moduleID), 0x00B0, 0x01, 0x02,
                                  0, 0)

    def openDoor(self, moduleID=2):
        self.excuteOrderRightAway("10号写指令", int(moduleID), 0x00B0, 0x01, 0x02,
                                  1, 0)

    # 彩灯
    def openColorfulLight(self, moduleID=5, lightMode=1, lightNum=50):
        self.excuteOrderRightAway("10号写指令", int(moduleID), 0x00AE, 0x02, 0x04,
                                  ((int(lightMode) << 16) | (int(lightNum))),
                                  0)

    def setColorfulLight(self, lightMode, lightNum):
        self.openColorfulLight(5, lightMode, lightNum)

    def closeColorfulLight(self, moduleID=5, lightMode=0, lightNum=255):
        self.excuteOrderRightAway("10号写指令", int(moduleID), 0x00AE, 0x02, 0x04,
                                  ((int(lightMode) << 16) | (int(lightNum))),
                                  0)

    # 窗帘
    def openCurtain(self, moduleID=1, cMode=1, cSpeed=0):
        self.excuteOrderRightAway("10号写指令", int(moduleID), 0x00B2, 0x02, 0x04,
                                  ((int(cMode) << 16) | (int(cSpeed))), 0)

    def setCurtain(self, cMode=None, cSpeed=None):
        self.openCurtain(1, cMode, cSpeed)

    def closeCurtain(self, moduleID=1):
        self.openCurtain(moduleID, 0, 0)

    # 警报
    def alarm(self, moduleID=6):
        self.excuteOrderRightAway("10号写指令", int(moduleID), 0x00A8, 0x01, 0x02,
                                  1, 0)

    def quitAlarm(self, moduleID=6):
        self.excuteOrderRightAway("10号写指令", int(moduleID), 0x00A8, 0x01, 0x02,
                                  0, 0)

    # 扩展风扇
    def openRoomFan(self, moduleID=3):
        self.excuteOrderRightAway("10号写指令", int(moduleID), 0x00AC, 0x01, 0x02,
                                  1, 0)

    def closeRoomFan(self, moduleID=3):
        self.excuteOrderRightAway("10号写指令", int(moduleID), 0x00AC, 0x01, 0x02,
                                  0, 0)

    # 垃圾桶
    def setServoAngle(self, moduleID=8, angle=0):
        if angle < 0:
            angle = 0
        elif angle > 180:
            angle = 180
        self.excuteOrderRightAway("10号写指令", int(moduleID), 0x00BE, 0x01, 0x02,
                                  angle, 0)

    def openAshcan(self, moduleID=8):
        self.setServoAngle(moduleID, 45)

    def closeAshcan(self, moduleID=8):
        self.setServoAngle(moduleID, 0)

    # 饮水机
    def openDrinkingFountain(self, moduleID=11):
        self.openRoomFan()

    def closeDrinkingFountain(self, moduleID=11):
        self.closeRoomFan()

    # 显示数字
    def displayTwoNum(self, moduleID=9, value1=0, value2=0):
        if value1 < 0:
            value1 = 0
        elif value1 > 0xFFFF:
            value1 = 0xFFFF

        if value2 < 0:
            value2 = 0
        elif value2 > 0xFFFF:
            value2 = 0xFFFF
        self.excuteOrderRightAway("10号写指令", int(moduleID), 0x00B2, 0x02, 0x04,
                                  ((int(value1) << 16) | (int(value2))), 0)

    # 显示交通灯信息
    def setTrafficLightMessage(self, moduleID=12, status=0, value=0):
        if status != 0:
            status = 1

        if value < 0:
            value = 0
        elif value > 0xFFFF:
            value = 0xFFFF
        self.excuteOrderRightAway("10号写指令", int(moduleID), 0x00C1, 0x02, 0x04,
                                  ((int(status) << 16) | (int(value))), 0)

    ################### 以下是获取状态 #####################
    # 单参数状态获取返回为true or false
    def isSingleStatusTrueOrFalse(self, moduleID=None, moduleAddr=0):
        recv_buf = self.queryOrder(1, "03号查询指令", int(moduleID), moduleAddr,
                                   0x01, 0)
        if recv_buf is not None:
            if recv_buf["data"]["数据"] == 1:
                return True
            else:
                return False
        else:
            return False

    # 报警器
    def isAlarming(self, moduleID=6):
        return self.isSingleStatusTrueOrFalse(moduleID, 0x00A8)

    # 灯光
    def isLightOpen(self, moduleID=4):
        return self.isSingleStatusTrueOrFalse(moduleID, 0x00AA)

    # 扩展风扇
    def isRoomFanOpen(self, moduleID=3):
        return self.isSingleStatusTrueOrFalse(moduleID, 0x00AC)

    # 门禁
    def isDoorOpen(self, moduleID=2):
        return self.isSingleStatusTrueOrFalse(moduleID, 0x00B0)

    # 窗帘
    def currentCurtainStatus(self, moduleID=1):
        recv_buf = self.queryOrder(1, "03号查询指令", int(moduleID), 0x00B2, 0x02,
                                   0)
        if recv_buf is not None:
            return [((recv_buf["data"]["数据"] >> 16) & 0xFFFF),
                    ((recv_buf["data"]["数据"]) & 0xFFFF)]
        else:
            return [-1, -1]

    def currentCurtainSpeed(self, moduleID=1):
        recv_buf = self.currentCurtainStatus(moduleID)
        if recv_buf[0] != -1 and recv_buf[1] != -1:
            return recv_buf[1]
        else:
            return -1

    def isCurtainOpen(self, moduleID=1):
        recv_buf = self.currentCurtainStatus(moduleID)
        if recv_buf[0] != -1 and recv_buf[1] != -1:
            if recv_buf[0] == 0:
                return True
            else:
                return False
        else:
            return False

    # 彩灯
    def currentColorfulLightStatus(self, moduleID=5):
        recv_buf = self.queryOrder(1, "03号查询指令", int(moduleID), 0x00AE, 0x02,
                                   0)
        if recv_buf is not None:
            return [((recv_buf["data"]["数据"] >> 16) & 0xFFFF),
                    ((recv_buf["data"]["数据"]) & 0xFFFF)]
        else:
            return [-1, -1]

    def isColorfulLightOpen(self, moduleID=5):
        recv_buf = self.currentColorfulLightStatus(moduleID)
        if recv_buf[0] != -1 and recv_buf[1] != -1:
            if recv_buf[0] != 0 and recv_buf[1] > 0:
                return True
            else:
                return False
        else:
            return False

    def currentColorfulLightMode(self, moduleID=5):
        recv_buf = self.currentColorfulLightStatus(moduleID)
        if recv_buf[0] != -1 and recv_buf[1] != -1:
            if recv_buf[0] == 0:
                return True
            else:
                return False
        else:
            return False

    def currentColorfulLightNum(self, moduleID=5):
        recv_buf = self.currentColorfulLightStatus(moduleID)
        if recv_buf[0] != -1 and recv_buf[1] != -1:
            return recv_buf[1]
        else:
            return -1

    def getRoomIRDegree(self, moduleID=5):
        return self.isSingleStatusTrueOrFalse(int(moduleID), 0x00B6)

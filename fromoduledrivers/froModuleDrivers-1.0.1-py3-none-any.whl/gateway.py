# -*- encoding=utf-8 -*-

from .baseDriver import BaseDriver
from .protocolHandler import *
from . import LOGGER
import time

tarVersion = "V20210823"

VersionDetail = "当前版本:" + tarVersion + """
---------------------------版本更新信息----------------------------

V20210818:
1.使用新的框架来实现旧的api，注意该版本并未实现节点号缺省功能

V20210823:
1、添加了硬件语音联动状态查询接口:def isSpeechAutoMode(self):
------------------------------------------------------------------
"""


class GatewayDict():
    last_speech = 0xFF
    gestureEncode = {0: "None", 1: "left", 2: "right", 3: "up", 4: "down"}
    voiceEncodeV2 = {
        # 0:"未识别到语音",
        # 1:"小飞同学",
        2: "打开灯光",
        3: "关闭灯光",
        4: "开一下灯",
        5: "关一下灯",
        6: "请开灯",
        7: "请关灯",
        8: "开始采摘",
        9: "开始运输",
        10: "开始入库",
        11: "开始出库",
        12: "播放音乐",
        13: "关闭音乐",
        14: "打开客厅灯光",
        15: "关闭客厅灯光",
        16: "打开厨房灯光",
        17: "关闭厨房灯光",
        18: "打开主人房灯光",
        19: "关闭主人房灯光",
        20: "打开客房灯光",
        21: "关闭客房灯光",
        22: "开启演示模式",
        23: "关闭演示模式",
        24: "打开路灯",
        25: "关闭路灯",
        26: "打开厕所灯光",
        27: "关闭厕所灯光",
        28: "娱乐模式",
        29: "学习模式",
        30: "打开所有灯光",
        31: "关闭所有灯光",
        32: "打开台灯",
        33: "关闭台灯",
        34: "上一首",
        35: "下一首",
        36: "打开儿童房灯光",
        37: "关闭儿童房灯光",
        38: "打开客厅窗帘",
        39: "关闭客厅窗帘",
        40: "客厅窗帘停止",
        41: "打开主人房窗帘",
        42: "关闭主人房窗帘",
        43: "主人房窗帘停止",
        44: "打开客房窗帘",
        45: "关闭客房窗帘",
        46: "客房窗帘停止",
        47: "打开书房窗帘",
        48: "关闭书房窗帘",
        49: "打开窗帘",
        50: "打开儿童房窗帘",
        51: "关闭儿童房窗帘",
        52: "关闭窗帘",
        53: "打开客厅风扇",
        54: "关闭客厅风扇",
        55: "打开主人房风扇",
        56: "关闭主人房风扇",
        57: "打开客房风扇",
        58: "关闭客房风扇",
        59: "打开书房风扇",
        60: "关闭书房风扇",
        61: "打开儿童房风扇",
        62: "关闭儿童房风扇",
        63: "打开通风",
        64: "关闭通风",
        65: "打开客厅门",
        66: "关闭客厅门",
        67: "打开主人房门",
        68: "关闭主人房门",
        69: "打开客房门",
        70: "关闭客房门",
        71: "打开厨房门",
        72: "关闭厨房门",
        73: "打开彩灯",
        74: "关闭彩灯",
        75: "最高亮度",
        76: "中等亮度",
        77: "最低亮度",
        78: "亮一点",
        79: "暗一点",
        80: "照明模式",
        81: "阅读模式",
        82: "夜灯模式",
        83: "红色模式",
        84: "绿色模式  ",
        85: "蓝色模式",
        86: "彩色模式",
        87: "流水灯模式",
        88: "打开防盗报警",
        89: "关闭防盗报警",
        90: "打开报警",
        91: "关闭报警",
        92: "打开空调",
        93: "关闭空调",
        94: "小车启动",
        95: "小车停止",
        96: "小车向前",
        97: "小车后退",
        98: "小车向左",
        99: "小车向右",
        100: "打开车灯",
        101: "开启避障",
        102: "关闭避障",
        103: "1号车启动",
        104: "2号车启动",
        105: "3号车启动",
        106: "4号车启动",
        107: "1号车停止",
        108: "2号车停止",
        109: "3号车停止",
        110: "4号车停止",
        111: "1号车进充电桩",
        112: "2号车进充电桩",
        113: "打开电视",
        114: "关闭电视",
        115: "上一台",
        116: "下一台",
        117: "1号车出充电桩",
        118: "2号车出充电桩",
        119: "晚安小飞",
        120: "早上好",
        121: "你好",
        122: "打开门",
        123: "关闭门",
        124: "打开风扇",
        125: "关闭风扇",
        126: "音量增",
        127: "我回来了",
        128: "我出去了",
        129: "进停车场",
        130: "出停车场",
        131: "开启布防",
        132: "撤销布防",
        133: "音量减",
        137: "大声点",
        138: "小声点",
        139: "最大声",
        140: "最小声",
    }


class GatewayDriver(BaseDriver, GatewayDict):
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
        # if result is None or result.get("data") is None:
        #     return None, False
        # else:
        #     LOGGER.logger.debug("doHandleResult:%s" % result)
        #     # if result["orderName"] == "03号查询指令":
        #     #     if result["data"].get("设备号") == 0x0101:
        #     #         print("my test", result["data"].get("数据"))
        #     # result["adiditon"] = "hello  world"
        #     return result, True

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

    ########################## 以下是网关节点配置方法 ############################
    def isSpeechAutoMode(self):
        return self.isSingleStatusTrueOrFalse(int(255), 0xff03)

    # 使能语音联动开关
    def enableSpeechAutoMode(self):
        self.excuteOrderRightAway("10号写指令", int(255), 0xff03, 0x01, 0x02, 1, 0)

    # 失能语音联动开关
    def disableSpeechAutoMode(self):
        self.excuteOrderRightAway("10号写指令", int(255), 0xff03, 0x01, 0x02, 0, 0)

    ########################## 以下是通用的执行器控制方法 ############################
    # 风扇
    def openFan(self, moduleID):
        self.excuteOrderRightAway("10号写指令", int(moduleID), 0x0048, 0x01, 0x02,
                                  1, 0)

    def closeFan(self, moduleID):
        self.excuteOrderRightAway("10号写指令", int(moduleID), 0x0048, 0x01, 0x02,
                                  0, 0)

    # RGB灯
    def openRGBLight(self, moduleID, redValue, greenValue, blueValue):
        self.excuteOrderRightAway("10号写指令", int(moduleID), 0x009e, 0x03, 0x06,
                                  ((int(redValue) & 0xFF) << 32) |
                                  ((int(greenValue) & 0xFF) << 16) |
                                  (int(blueValue) & 0xFF), 0)

    # todo
    # def setRGBLight(self, redValue=None, greenValue=None, blueValue=None):
    #     self.openRGBLight(self, moduleID, redValue, greenValue, blueValue)

    def setRGBRed(self, redValue, moduleID):
        self.openRGBLight(moduleID, redValue, 0, 0)

    def setRGBGreen(self, greenValue, moduleID):
        self.openRGBLight(moduleID, 0, greenValue, 0)

    def setRGBBlue(self, blueValue, moduleID):
        self.openRGBLight(moduleID, 0, 0, blueValue)

    def closeRGBLight(self, moduleID=None):
        self.excuteOrderRightAway("10号写指令", int(moduleID), 0x009e, 0x03, 0x06,
                                  0, 0)

    # 蜂鸣器
    def playAudioPlayer(self, moduleID, songID=1, songVolume=100):
        if songID != None and songVolume != None:
            if songID <= 0 or songID > 5 or songVolume < 0 or songVolume > 100:
                return
        else:
            return
        self.excuteOrderRightAway("10号写指令", int(moduleID), 0x0096, 0x02, 0x04,
                                  ((int(songID) << 16) | (int(songVolume))), 0)

    def playSongBySongID(self, moduleID, songID):
        self.playAudioPlayer(int(moduleID), int(songID), 100, 0)

    # todo
    # def playSong(self, songID, songVolumn):
    #     self.playAudioPlayer(None, songID, songVolumn)

    def stopAudioPlayer(self, moduleID):
        self.excuteOrderRightAway("10号写指令", int(moduleID), 0x0096, 0x02, 0x04,
                                  0x00000000, 0)

    # 红外转发
    def sendIRTrans(self, moduleID, param):
        param = param % 14
        if param in [7, 8, 9]:
            return
        self.excuteOrderRightAway("10号写指令", int(moduleID), 0x009A, 0x01, 0x02,
                                  param, 0)

    def addChannel(self, moduleID=None):
        param = 10
        self.excuteOrderRightAway("10号写指令", int(moduleID), 0x009A, 0x01, 0x02,
                                  param, 0)

    def descChannel(self, moduleID=None):
        param = 11
        self.excuteOrderRightAway("10号写指令", int(moduleID), 0x009A, 0x01, 0x02,
                                  param, 0)

    def addVolumn(self, moduleID=None):
        param = 13
        self.excuteOrderRightAway("10号写指令", int(moduleID), 0x009A, 0x01, 0x02,
                                  param, 0)

    def descVolumn(self, moduleID=None):
        param = 12
        self.excuteOrderRightAway("10号写指令", int(moduleID), 0x009A, 0x01, 0x02,
                                  param, 0)

    ################### 以下是获取状态 #####################

    # 手势
    def checkGesture(self, moduleID):
        recv_buf = self.queryOrder(1, "03号查询指令", int(moduleID), 0x00A6, 0x01,
                                   0)
        if recv_buf is not None:
            return self.gestureEncode[recv_buf["data"]["数据"]]
        else:
            return False

    # 语音识别
    def recognizeSpeech(self, moduleID=None):
        recv_buf = self.queryOrder(1, "03号查询指令", int(moduleID), 0x00b8, 0x01,
                                   0)
        current_speech = recv_buf["data"]["数据"]
        if self.last_speech != current_speech:
            self.last_speech = current_speech
            # self.log("e",current_speech)
            if self.last_speech in self.voiceEncodeV2:
                return self.last_speech
        return False

    # 场景代码-红外对射场景
    def getIRDegree(self, moduleID):
        recv_buf = self.queryOrder(1, "03号查询指令", int(moduleID), 0x002C, 0x01,
                                   0)
        if recv_buf is not None:
            if recv_buf["data"]["数据"] == 1:
                return True
            else:
                return False
        else:
            return False

    # 场景代码-红外反射传感器
    def getAIRDegree(self, moduleID):
        recv_buf = self.queryOrder(1, "03号查询指令", int(moduleID), 0x0036, 0x01,
                                   0)
        if recv_buf is not None:
            if recv_buf["data"]["数据"] == 1:
                return True
            else:
                return False
        else:
            return False

    # 场景代码-红外转发
    def getIRSend(self, moduleID):
        recv_buf = self.queryOrder(1, "03号查询指令", int(moduleID), 0x009A, 0x01,
                                   0)
        if recv_buf is not None:
            return recv_buf["data"]["数据"]
        else:
            return False

    # 场景代码-红外接收
    def getIRRecv(self, moduleID):
        recv_buf = self.queryOrder(1, "03号查询指令", int(moduleID), 0x009C, 0x01,
                                   0)
        if recv_buf is not None:
            return recv_buf["data"]["数据"]
        else:
            return False

    # 场景代码-人体
    def checkHuman(self, moduleID):
        recv_buf = self.queryOrder(1, "03号查询指令", int(moduleID), 0x003C, 0x01,
                                   0)
        if recv_buf is not None:
            if recv_buf["data"]["数据"] == 1:
                return True
            else:
                return False
        else:
            return False

    # 场景代码-获取光照值场景
    def getShineDegree(self, moduleID):
        recv_buf = self.queryOrder(1, "03号查询指令", int(moduleID), 0x002A, 0x01,
                                   0)
        if recv_buf is not None:
            return recv_buf["data"]["数据"]
        else:
            return 0

    # 场景代码-烟雾
    def checkSmoke(self, moduleID):
        recv_buf = self.queryOrder(1, "03号查询指令", int(moduleID), 0x0034, 0x01,
                                   0)
        if recv_buf is not None:
            return recv_buf["data"]["数据"]
        else:
            return 0

    # 场景代码-声音
    def checkSound(self, moduleID):
        recv_buf = self.queryOrder(1, "03号查询指令", int(moduleID), 0x003A, 0x01,
                                   0)
        if recv_buf is not None:
            if recv_buf["data"]["数据"] == 1:
                return True
            else:
                return False
        else:
            return False

    # 场景代码-结露
    def checkRain(self, moduleID):
        recv_buf = self.queryOrder(1, "03号查询指令", int(moduleID), 0x002E, 0x01,
                                   0)
        if recv_buf is not None:
            return recv_buf["data"]["数据"]
        else:
            return -1

    # 场景代码-火焰
    def checkFire(self, moduleID):
        recv_buf = self.queryOrder(1, "03号查询指令", int(moduleID), 0x0038, 0x01,
                                   0)
        if recv_buf is not None:
            if recv_buf["data"]["数据"] == 1:
                return True
            else:
                return False
        else:
            return False

    # 场景代码-燃气
    def checkCGas(self, moduleID=None):
        recv_buf = self.queryOrder(1, "03号查询指令", int(moduleID), 0x00A4, 0x01,
                                   0)
        if recv_buf is not None:
            return recv_buf["data"]["数据"]
        else:
            return -1

    # 场景代码-温湿度
    def getTemperatureHumidity(self, moduleID):
        recv_buf = self.queryOrder(1, "03号查询指令", int(moduleID), 0x0014, 0x02,
                                   0)
        if recv_buf is not None:
            return [((recv_buf["data"]["数据"] >> 16) & 0xFFFF) / 10.0,
                    ((recv_buf["data"]["数据"]) & 0xFFFF) / 10.0]
        else:
            return [-1, -1]

    # 场景代码-温度
    def getTemperature(self, moduleID):
        recv_buf = self.getTemperatureHumidity(moduleID)
        if recv_buf[0] != -1 and recv_buf[1] != -1:
            return recv_buf[0]
        else:
            return -1

    # 场景代码-湿度
    def getHumidity(self, moduleID):
        recv_buf = self.getTemperatureHumidity(moduleID)
        if recv_buf[0] != -1 and recv_buf[1] != -1:
            return recv_buf[1]
        else:
            return -1

    ################### 以下是执行器状态查询 #####################

    def isFanOpen(self, moduleID):
        recv_buf = self.queryOrder(1, "03号查询指令", int(moduleID), 0x0048, 0x01,
                                   0)
        if recv_buf is not None:
            if recv_buf["data"]["数据"] == 1:
                return True
            else:
                return False
        else:
            return False

    def isRGBLightOpen(self, moduleID):
        recv_buf = self.queryOrder(1, "03号查询指令", int(moduleID), 0x009e, 0x03,
                                   0)
        if recv_buf is not None:
            if recv_buf["data"]["数据"] != 0:
                return True
            else:
                return False
        else:
            return False

    def currentRGBLight(self, moduleID):
        recv_buf = self.queryOrder(1, "03号查询指令", int(moduleID), 0x009e, 0x03,
                                   0)
        if recv_buf is not None:
            return [((recv_buf["data"]["数据"] >> 32) & 0xFFFF),
                    ((recv_buf["data"]["数据"] >> 16) & 0xFFFF),
                    ((recv_buf["data"]["数据"]) & 0xFFFF)]
        else:
            return [-1, -1, -1]

    def getRGBRed(self, moduleID):
        recv_buf = self.currentRGBLight(moduleID)
        if recv_buf[0] != -1 and recv_buf[1] != -1 and recv_buf[2] != -1:
            return recv_buf[0]
        else:
            return -1

    def getRGBGreen(self, moduleID=None):
        recv_buf = self.currentRGBLight(moduleID)
        if recv_buf[0] != -1 and recv_buf[1] != -1 and recv_buf[2] != -1:
            return recv_buf[1]
        else:
            return -1

    def getRGBBlue(self, moduleID=None):
        recv_buf = self.currentRGBLight(moduleID)
        if recv_buf[0] != -1 and recv_buf[1] != -1 and recv_buf[2] != -1:
            return recv_buf[2]
        else:
            return -1

    def audioPlayerCurrentPlayed(self, moduleID):
        recv_buf = self.queryOrder(1, "03号查询指令", int(moduleID), 0x0096, 0x02,
                                   0)
        if recv_buf is not None:
            return [((recv_buf["data"]["数据"] >> 16) & 0xFFFF),
                    ((recv_buf["data"]["数据"]) & 0xFFFF)]
        else:
            return [-1, -1]

    def audioPlayerCurrentPlayedSong(self, moduleID):
        recv_buf = self.audioPlayerCurrentPlayed(moduleID)
        if recv_buf[0] != -1 and recv_buf[1] != -1:
            return recv_buf[0]
        else:
            return -1

    def audioPlayerCurrentPlayedVolumn(self, moduleID=None):
        recv_buf = self.audioPlayerCurrentPlayed(moduleID)
        if recv_buf[0] != -1 and recv_buf[1] != -1:
            return recv_buf[1]
        else:
            return -1

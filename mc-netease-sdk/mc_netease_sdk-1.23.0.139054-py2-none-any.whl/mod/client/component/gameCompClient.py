# -*- coding: utf-8 -*-

from typing import Tuple
from typing import Union
from mod.common.utils.timer import CallLater
from typing import List
from typing import Any
from mod.common.component.baseComponent import BaseComponent

class GameComponentClient(BaseComponent):
    def ShowHealthBar(self, show):
        # type: (bool) -> bool
        """
        设置是否显示血条
        """
        pass

    def SetNameDeeptest(self, deeptest):
        # type: (bool) -> bool
        """
        设置名字是否透视
        """
        pass

    def GetScreenSize(self):
        # type: () -> Tuple[float,float]
        """
        获取游戏分辨率
        """
        pass

    def SetRenderLocalPlayer(self, render):
        # type: (bool) -> bool
        """
        设置本地玩家是否渲染
        """
        pass

    def AddPickBlacklist(self, entityId):
        # type: (str) -> bool
        """
        添加使用camera组件选取实体时的黑名单，即该实体不会被选取到
        """
        pass

    def ClearPickBlacklist(self):
        # type: () -> bool
        """
        清除使用camera组件选取实体的黑名单
        """
        pass

    def GetEntityInArea(self, entityId, pos_a, pos_b, exceptEntity=False):
        # type: (Union[str,None], Tuple[int,int,int], Tuple[int,int,int], bool) -> List[str]
        """
        返回区域内的实体，可获取到区域范围内已加载的实体列表
        """
        pass

    def HasEntity(self, entityId):
        # type: (str) -> int
        """
        判断 entity 是否存在
        """
        pass

    def IsEntityAlive(self, entityId):
        # type: (str) -> bool
        """
        判断生物实体是否存活或非生物实体是否存在
        """
        pass

    def CheckWordsValid(self, words):
        # type: (str) -> bool
        """
        检查语句是否合法，即不包含敏感词
        """
        pass

    def CheckNameValid(self, name):
        # type: (str) -> bool
        """
        检查昵称是否合法，即不包含敏感词
        """
        pass

    def GetScreenViewInfo(self):
        # type: () -> Tuple[float,float,float,float]
        """
        获取游戏视角信息。分辨率为1313，618时，画布是376，250的2倍，所以viewport得到的是1313 + (2-(1313%2))，y值类似，可参考《我的世界》界面适配方法
        """
        pass

    def SetPopupNotice(self, message, subtitle):
        # type: (str, str) -> bool
        """
        在本地玩家的物品栏上方弹出popup类型通知，位置位于tip类型消息下方
        """
        pass

    def SetTipMessage(self, message):
        # type: (str) -> bool
        """
        在本地玩家的物品栏上方弹出tip类型通知，位置位于popup类型通知上方
        """
        pass

    def AddTimer(self, delay, func, *args, **kwargs):
        # type: (float, function, Any, Any) -> CallLater
        """
        添加客户端触发的定时器，非重复
        """
        pass

    def AddRepeatedTimer(self, delay, func, *args, **kwargs):
        # type: (float, function, Any, Any) -> CallLater
        """
        添加客户端触发的定时器，重复执行
        """
        pass

    def CancelTimer(self, timer):
        # type: (CallLater) -> None
        """
        取消定时器
        """
        pass

    def SimulateTouchWithMouse(self, touch):
        # type: (bool) -> bool
        """
        模拟使用鼠标控制UI（PC F11快捷键）
        """
        pass

    def GetCurrentDimension(self):
        # type: () -> int
        """
        获取客户端当前维度
        """
        pass

    def GetChinese(self, langStr):
        # type: (str) -> str
        """
        获取langStr对应的中文，可参考PC开发包中\handheld\bed-loc\handheld\data\resource_packs\vanilla\texts\zh_CN.lang
        """
        pass


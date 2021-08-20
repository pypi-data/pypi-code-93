# -*- coding: utf-8 -*-

from Preset.Model.GameObject import GameObject
from Preset.Model.PresetBase import PresetBase
from Preset.Model.TransformObject import TransformObject
from Preset.Model.SdkInterface import SdkInterface

class PartBase(TransformObject, SdkInterface):
    def __init__(self):
        # type: () -> None
        """
        PartBase（零件基类）是可以与零件进行绑定，而零件可以挂接在预设下，以实现带逻辑的预设的组装。所有的自定义零件都需要继承PartBase，预设系统下的大部分代码都需要写在自定义零件中。注意，自定义零件只有挂接到预设，并且在游戏中实例化才能生效。
        """
        self.tickEnable = None
        self.replicated = None

    def InitClient(self):
        # type: () -> None
        """
        客户端的零件对象初始化入口
        """
        pass

    def InitServer(self):
        # type: () -> None
        """
        服务端的零件对象初始化入口
        """
        pass

    def TickClient(self):
        # type: () -> None
        """
        客户端的零件对象逻辑驱动入口
        """
        pass

    def TickServer(self):
        # type: () -> None
        """
        服务端的零件对象逻辑驱动入口
        """
        pass

    def UnloadClient(self):
        # type: () -> None
        """
        客户端的零件对象卸载逻辑入口
        """
        pass

    def UnloadServer(self):
        # type: () -> None
        """
        服务端的零件对象卸载逻辑入口
        """
        pass

    def DestroyClient(self):
        # type: () -> None
        """
        客户端的零件对象销毁逻辑入口
        """
        pass

    def DestroyServer(self):
        # type: () -> None
        """
        服务端的零件对象销毁逻辑入口
        """
        pass

    def CanAdd(self, parent):
        # type: (PresetBase) -> str
        """
        判断零件是否可以挂接到指定的父节点上
        """
        pass

    def GetTickCount(self):
        # type: () -> int
        """
        获取当前帧数
        """
        pass

    def GetGameObjectById(self, id):
        # type: (int) -> GameObject
        """
        获取指定对象ID的游戏对象
        """
        pass

    def GetGameObjectByEntityId(self, entityId):
        # type: (str) -> GameObject
        """
        获取指定实体ID的游戏对象
        """
        pass

    def CreateGameObjectByEntityId(self, entityId):
        # type: (str) -> GameObject
        """
        获根据指定实体ID创建游戏对象，已存在则直接返回
        """
        pass

    def ListenForEvent(self, namespace, systemName, eventName, instance, func, priority=0):
        # type: (str, str, str, object, object, str) -> None
        """
        监听指定的事件
        """
        pass

    def UnListenForEvent(self, namespace, systemName, eventName, instance, func, priority=0):
        # type: (str, str, str, object, object, str) -> None
        """
        反监听指定的事件
        """
        pass

    def DefineEvent(self, eventName):
        # type: (str) -> None
        """
        定义事件
        """
        pass

    def UnDefineEvent(self, eventName):
        # type: (str) -> None
        """
        反定义事件
        """
        pass

    def CreateEventData(self):
        # type: () -> dict
        """
        创建自定义事件的数据，eventData用于发送事件。创建的eventData可以理解为一个dict，可以嵌套赋值dict,list和基本数据类型，但不支持tuple
        """
        pass

    def BroadcastEvent(self, eventName, eventData):
        # type: (str, object) -> None
        """
        广播事件，双端通用
        """
        pass

    def BroadcastClientEvent(self, eventName, eventData):
        # type: (str, object) -> None
        """
        广播给所有客户端
        """
        pass

    def BroadcastServerEvent(self, eventName, eventData):
        # type: (str, object) -> None
        """
        广播给所有服务端
        """
        pass

    def NotifyToServer(self, eventName, eventData):
        # type: (str, object) -> None
        """
        通知服务端触发事件
        """
        pass

    def NotifyToClient(self, playerId, eventName, eventData):
        # type: (str, str, object) -> None
        """
        通知指定客户端触发事件
        """
        pass

    def BroadcastToAllClient(self, eventName, eventData):
        # type: (str, object) -> None
        """
        通知指所有客户端触发事件
        """
        pass

    def ListenSelfEvent(self, eventName, target, func):
        # type: (str, object, object) -> None
        """
        监听来自自己的事件
        """
        pass

    def UnListenSelfEvent(self, eventName, target, func):
        # type: (str, object, object) -> None
        """
        反监听来自自己的事件
        """
        pass

    def ListenPartEvent(self, partId, eventName, target, func):
        # type: (int, str, object, object) -> None
        """
        监听来自指定零件的事件
        """
        pass

    def UnListenPartEvent(self, partId, eventName, target, func):
        # type: (int, str, object, object) -> None
        """
        反监听来自指定零件的事件
        """
        pass


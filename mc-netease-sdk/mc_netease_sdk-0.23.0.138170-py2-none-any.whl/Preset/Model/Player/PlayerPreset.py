# -*- coding: utf-8 -*-

from Preset.Model.Entity.EntityPreset import EntityPreset
from typing import Tuple

class PlayerPreset(EntityPreset):
    def __init__(self):
        # type: () -> None
        """
        PlayerPreset（玩家预设）是一类特殊的实体预设，玩家预设与玩家实体进行绑定。每个AddOn（编辑器作品）只允许创建一个玩家预设。如果玩家同时启用了多个使用了玩家预设的AddOn，只会加载第一个玩家预设。
        """
        self.entityId = None

    def GetPlayerId(self):
        # type: () -> str
        """
        获取玩家预设的玩家ID
        """
        pass

    def IsSneaking(self):
        # type: () -> bool
        """
        是否潜行
        """
        pass

    def GetHunger(self):
        # type: () -> float
        """
        获取玩家饥饿度，展示在UI饥饿度进度条上，初始值为20，即每一个鸡腿代表2个饥饿度。 **饱和度(saturation)** ：玩家当前饱和度，初始值为5，最大值始终为玩家当前饥饿度(hunger)，该值直接影响玩家**饥饿度(hunger)**。<br>1）增加方法：吃食物。<br>2）减少方法：每触发一次**消耗事件**，该值减少1，如果该值不大于0，直接把玩家 **饥饿度(hunger)** 减少1。
        """
        pass

    def SetHunger(self, value):
        # type: (float) -> bool
        """
        设置玩家饥饿度。
        """
        pass

    def SetMotion(self, motion):
        # type: (Tuple[float,float,float]) -> bool
        """
        设置生物（不含玩家）的瞬时移动方向向量
        """
        pass

    def GetMotion(self):
        # type: () -> Tuple[int,int,int]
        """
        获取生物（含玩家）的瞬时移动方向向量
        """
        pass

    def SetStepHeight(self, stepHeight):
        # type: (float) -> bool
        """
        设置玩家前进非跳跃状态下能上的最大台阶高度, 默认值为0.5625，1的话表示能上一个台阶
        """
        pass

    def GetStepHeight(self):
        # type: () -> float
        """
        返回玩家前进非跳跃状态下能上的最大台阶高度
        """
        pass

    def ResetStepHeight(self):
        # type: () -> bool
        """
        恢复引擎默认玩家前进非跳跃状态下能上的最大台阶高度
        """
        pass

    def GetExp(self, isPercent=True):
        # type: (bool) -> float
        """
        获取玩家当前等级下的经验值
        """
        pass

    def AddExp(self, exp):
        # type: (int) -> bool
        """
        增加玩家经验值
        """
        pass

    def GetTotalExp(self):
        # type: () -> int
        """
        获取玩家的总经验值
        """
        pass

    def SetTotalExp(self, exp):
        # type: (int) -> bool
        """
        设置玩家的总经验值
        """
        pass

    def IsFlying(self):
        # type: () -> bool
        """
        获取玩家是否在飞行
        """
        pass

    def ChangeFlyState(self, isFly):
        # type: (bool) -> bool
        """
        给予/取消飞行能力，并且进入飞行/非飞行状态
        """
        pass

    def GetLevel(self):
        # type: () -> int
        """
        获取玩家等级
        """
        pass

    def AddLevel(self, level):
        # type: (int) -> bool
        """
        修改玩家等级
        """
        pass

    def SetPrefixAndSuffixName(self, prefix, prefixColor, suffix, suffixColor):
        # type: (str, str, str, str) -> bool
        """
        设置玩家前缀和后缀名字
        """
        pass


# -*- coding: utf-8 -*-

from mod.common.component.baseComponent import BaseComponent

class AttrCompServer(BaseComponent):
    def SetAttrValue(self, attrType, value):
        # type: (int, float) -> bool
        """
        设置属性值，包括生命值，饥饿度，移速
        """
        pass

    def GetAttrValue(self, attrType):
        # type: (int) -> float
        """
        获取属性值，包括生命值，饥饿度，移速
        """
        pass

    def SetAttrMaxValue(self, type, value):
        # type: (int, float) -> bool
        """
        设置属性最大值，包括生命值，饥饿度，移速
        """
        pass

    def GetAttrMaxValue(self, type):
        # type: (int) -> float
        """
        获取属性最大值，包括生命值，饥饿度，移速
        """
        pass

    def IsEntityOnFire(self):
        # type: () -> bool
        """
        获取实体是否着火
        """
        pass

    def SetEntityOnFire(self, seconds, burn_damage=1):
        # type: (int, int) -> bool
        """
        设置实体着火
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


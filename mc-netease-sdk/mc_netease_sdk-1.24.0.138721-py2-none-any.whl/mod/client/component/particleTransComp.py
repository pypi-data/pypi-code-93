# -*- coding: utf-8 -*-

from mod.common.component.baseComponent import BaseComponent
from typing import Tuple

class ParticleTransComp(BaseComponent):
    def GetPos(self):
        # type: () -> Tuple[float,float,float]
        """
        获取粒子发射器的世界坐标位置
        """
        pass

    def SetPos(self, pos):
        # type: (Tuple[float,float,float]) -> bool
        """
        设置粒子发射器的世界坐标位置
        """
        pass

    def GetRot(self):
        # type: () -> Tuple[float,float,float]
        """
        获取粒子发射器的旋转角度
        """
        pass

    def SetRot(self, pos):
        # type: (Tuple[float,float,float]) -> bool
        """
        设置粒子发射器的旋转
        """
        pass


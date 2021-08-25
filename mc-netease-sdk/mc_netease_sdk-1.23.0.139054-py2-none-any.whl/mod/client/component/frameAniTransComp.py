# -*- coding: utf-8 -*-

from mod.common.component.baseComponent import BaseComponent
from typing import Tuple

class FrameAniTransComp(BaseComponent):
    def SetPos(self, pos):
        # type: (Tuple[float,float,float]) -> bool
        """
        设置序列帧的位置
        """
        pass

    def SetRot(self, rot):
        # type: (Tuple[float,float,float]) -> bool
        """
        设置序列帧的旋转
        """
        pass

    def SetScale(self, scale):
        # type: (Tuple[float,float,float]) -> bool
        """
        设置序列帧的缩放
        """
        pass


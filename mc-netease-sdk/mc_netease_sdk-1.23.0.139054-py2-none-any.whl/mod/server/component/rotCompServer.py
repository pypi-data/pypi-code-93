# -*- coding: utf-8 -*-

from typing import Tuple

class RotComponentServer(object):
    def SetRot(self, rot):
        # type: (Tuple[float,float]) -> bool
        """
        设置实体角度
        """
        pass

    def GetRot(self):
        # type: () -> Tuple[float,float]
        """
        获取实体角度
        """
        pass

    def SetEntityLookAtPos(self, targetPos, minTime, maxTime, reject):
        # type: (Tuple[float,float,float], float, float, bool) -> bool
        """
        设置非玩家的实体看向某个位置
        """
        pass


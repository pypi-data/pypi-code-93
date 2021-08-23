# -*- coding: utf-8 -*-

from mod.common.component.baseComponent import BaseComponent
from typing import Tuple

class PostProcessComponent(BaseComponent):
    def SetEnableVignette(self, enable):
        # type: (bool) -> bool
        """
        设置是否开启Vignette屏幕渐晕效果，开启后玩家屏幕周围将出现渐晕，可通过Vignette其他接口设置效果参数。未调用SetEnablePostProcess接口开启屏幕后处理效果之前将无法生效。
        """
        pass

    def CheckVigneteEnabled(self):
        # type: () -> bool
        """
        检测是否开启了Vignette屏幕渐晕效果。
        """
        pass

    def SetVignetteRGB(self, color):
        # type: (Tuple[float,float,float]) -> bool
        """
        设置Vignette效果的渐晕颜色，可改变屏幕渐晕的颜色。
        """
        pass

    def SetVignetteCenter(self, center):
        # type: (Tuple[float,float]) -> bool
        """
        设置Vignette效果的渐晕中心位置，可改变屏幕渐晕的位置。
        """
        pass

    def SetVignetteRadius(self, radius):
        # type: (float) -> bool
        """
        设置Vignette效果的渐晕半径，半径越大，渐晕越小，玩家的视野范围越大。
        """
        pass

    def SetVignetteSmoothness(self, radius):
        # type: (float) -> bool
        """
        设置Vignette效果的渐晕模糊系数，模糊系数越大，则渐晕边缘越模糊，模糊的范围也越大
        """
        pass


# -*- coding: utf-8 -*-

from mod.client.ui.controls.baseUIControl import BaseUIControl
from typing import Tuple

class LabelUIControl(BaseUIControl):
    def SetText(self, text, syncSize=False):
        # type: (str, bool) -> None
        """
        设置Label的文本信息
        """
        pass

    def GetText(self):
        # type: () -> str
        """
        获取Label的文本信息，获取失败会返回None
        """
        pass

    def SetTextColor(self, color):
        # type: (Tuple[float,float,float,float]) -> None
        """
        设置Label文本的颜色
        """
        pass

    def GetTextColor(self):
        # type: () -> Tuple[float,float,float,float]
        """
        获取Label文本颜色
        """
        pass

    def SetTextFontSize(self, componentPath, scale):
        # type: (str, float) -> None
        """
        设置Label中文本字体的大小
        """
        pass


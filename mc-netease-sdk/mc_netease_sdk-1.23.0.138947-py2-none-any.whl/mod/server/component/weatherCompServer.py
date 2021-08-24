# -*- coding: utf-8 -*-

from mod.common.component.baseComponent import BaseComponent

class WeatherComponentServer(BaseComponent):
    def IsRaining(self):
        # type: () -> bool
        """
        获取是否下雨
        """
        pass

    def SetRaining(self, level, time):
        # type: (float, int) -> bool
        """
        设置是否下雨
        """
        pass

    def SetThunder(self, level, time):
        # type: (float, int) -> bool
        """
        设置是否打雷
        """
        pass

    def IsThunder(self):
        # type: () -> bool
        """
        获取是否打雷
        """
        pass


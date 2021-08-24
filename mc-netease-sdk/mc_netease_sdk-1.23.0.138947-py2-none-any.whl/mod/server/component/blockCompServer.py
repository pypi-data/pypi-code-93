# -*- coding: utf-8 -*-

from typing import List
from mod.common.component.baseComponent import BaseComponent
from typing import Tuple

class BlockCompServer(BaseComponent):
    def RegisterBlockPatterns(self, pattern, defines, result_actor_name):
        # type: (List[str], dict, str) -> bool
        """
        注册特殊方块组合
        """
        pass

    def CreateMicroBlockResStr(self, identifier, start, end, colorMap=None, isMerge=False, icon=''):
        # type: (str, Tuple[int,int,int], Tuple[int,int,int], dict, bool, str) -> str
        """
        生成微缩方块资源Json字符串
        """
        pass


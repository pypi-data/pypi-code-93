# -*- coding: utf-8 -*-

from typing import Union
from mod.common.component.baseComponent import BaseComponent
from typing import Tuple

class BlockInfoComponentClient(BaseComponent):
    def GetBlock(self, pos):
        # type: (Tuple[float,float,float]) -> Tuple[str,int]
        """
        获取某一位置的block
        """
        pass

    def GetTopBlockHeight(self, pos):
        # type: (Tuple[int,int]) -> Union[int,None]
        """
        获取当前维度某一位置最高的非空气方块的高度
        """
        pass

    def ChangeBlockTextures(self, blockName, tileName, texturePath):
        # type: (str, str, str) -> bool
        """
        替换方块贴图
        """
        pass

    def GetDestroyTotalTime(self, blockName, itemName=None):
        # type: (str, str) -> float
        """
        获取使用物品破坏方块需要的时间
        """
        pass


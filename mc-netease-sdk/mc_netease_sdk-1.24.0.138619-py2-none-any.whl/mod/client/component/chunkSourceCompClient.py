# -*- coding: utf-8 -*-

from typing import Union
from mod.common.component.baseComponent import BaseComponent
from typing import Tuple

class ChunkSourceCompClient(BaseComponent):
    def RemoveChunkPosWhiteList(self, dimensionId, pos):
        # type: (int, Tuple[int,int]) -> bool
        """
        移除对某区块加载完成、准备卸载事件的监听
        """
        pass

    def GetChunkPosFromBlockPos(self, blockPos):
        # type: (Tuple[int,int,int]) -> Union[None,Tuple[int,int]]
        """
        通过方块坐标获得该方块所在区块坐标
        """
        pass


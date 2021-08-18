# -*- coding: utf-8 -*-

from mod.common.component.baseComponent import BaseComponent

class AttrCompClient(BaseComponent):
    def isEntityInLava(self):
        # type: () -> bool
        """
        实体是否在岩浆中
        """
        pass

    def isEntityOnGround(self):
        # type: () -> bool
        """
        实体是否触地
        """
        pass


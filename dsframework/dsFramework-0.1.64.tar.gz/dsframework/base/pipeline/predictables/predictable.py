#!/usr/bin/env python
# coding: utf-8

from typing import Any
from dsframework.base.common import ZIDS_Object

class ZIDS_Predictable(ZIDS_Object):

    def __init__(self) -> None:
        super().__init__()
        self.name:str = ''
        self.input:Any = None
        self.target:Any = None    
        self.pred: Any = None
        self.prob:float = -1.0
        self.forced_pred:Any = None
        self.forced_reason:str = 'Did Not Forced'

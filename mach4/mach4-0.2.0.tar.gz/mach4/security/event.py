# -*- coding: utf-8 -*-
"""
Created on Fri Feb 19 14:39:45 2021

@author: Cyriaque Perier
"""

from enum import Enum

class EventType(Enum):
    
    """
    
    Enumeration of all events types
    
    """
    
    ADD_JWT_KEY = "Add JWT key"
    ADD_XSRF_KEY = "Add XSRF key"
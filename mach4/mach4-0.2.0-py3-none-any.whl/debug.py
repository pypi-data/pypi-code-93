# -*- coding: utf-8 -*-
"""
Created on Sun Aug 22 14:24:44 2021

Copyright 2021 Cyriaque Perier

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import time
from mach4.utils import Colors

def int_to_text(integer):
    
    if integer < 10:
        
        integer = "0" + str(integer)
    
    else:
        integer = str(integer)
    
    return integer

class Debug:
    
    """
    
    Debug message manager
    
    """
    
    def __init__(self, enabled):
        
        self.enabled = enabled
    
    def log(self, label, message):
        
        if self.enabled:
            
            gmt = time.gmtime(time.time())
            
            time_label = "({}/{}/{} {}:{}:{})".format(
                    gmt.tm_year, int_to_text(gmt.tm_mday), 
                    int_to_text(gmt.tm_mon), int_to_text(gmt.tm_hour), 
                    int_to_text(gmt.tm_min), int_to_text(gmt.tm_sec)
                    )
            log_text = "{}{} [Mach4:{}] {}{}".format(Colors.WHITE, time_label, label, message, Colors.RESET)
            
            print(log_text)
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 20 11:49:30 2021

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

import requests

class HCaptchaInstance:
    
    """
    
    Integrity checking instance for hCaptcha anti-bots
    
    """
    
    def __init__(self, verify_url="https://hcaptcha.com/siteverify", secret=None):
        
        
        """
        
        Initialise object
        
        """
        
        self.verify_url = verify_url
        self.secret = secret
        
    def verify(self, response, remote_ip=None, site_key=None, secret=None):
        
        if secret is None:
            
            secret = self.secret
        
        verify_data = {
                "secret" : secret,
                "response" : response,
                "remoteip" : remote_ip,
                "sitekey" : site_key
                }
        
        verify_query = requests.post(self.verify_url, data=verify_data)
        
        return verify_query.json()
    

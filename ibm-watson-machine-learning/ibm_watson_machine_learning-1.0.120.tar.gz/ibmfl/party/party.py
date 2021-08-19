"""
IBM Confidential
OCO Source Materials
5737-H76, 5725-W78, 5900-A1R
(c) Copyright IBM Corp. 2020 All Rights Reserved.
The source code for this program is not published or otherwise divested of its trade secrets,
irrespective of what has been deposited with the U.S. Copyright Office.
"""
#!/usr/bin/env python3
import os
import sys
import importlib.util

def import_source(module_file_path):
    module_name = 'ibmfl'
    
    module_spec = importlib.util.spec_from_file_location(
        module_name, module_file_path)
    module = importlib.util.module_from_spec(module_spec)
    sys.modules[module_name] = module
    module_spec.loader.exec_module(module)


fl_path = os.path.abspath('.')
if fl_path not in sys.path:
    sys.path.append(fl_path)



class Party:
    """
    Party Wrapper for determining required version of FL Party to invoke.
    """

    SUPPORTED_PLATFORMS_MAP = {
        'cloud':"/cloud/ibmfl/__init__.py",
        'cpd35':"/cpd35/ibmfl/__init__.py",
    } 

    def __init__(self, **kwargs):
        ibmfl_module = sys.modules['ibmfl'] 
        ibmfl_module_location_list = ibmfl_module.__path__
        
        # base location string, default to cloud location 
        ibmfl_module_location = ibmfl_module_location_list[0] 
        
        # get arg for platform
        platform_env = kwargs.get('env', 'cloud')
        api_client = kwargs.get('apiclient', None)
        if api_client is not None and api_client.ICP_35 == True:
            platform_env = 'cpd35'

        
        # process location 
        ibmfl_module_location = ibmfl_module_location + self.SUPPORTED_PLATFORMS_MAP.get(platform_env)
        
        del sys.modules['ibmfl']
        del sys.modules['ibmfl.party']
        del sys.modules['ibmfl.party.party']
        import_source(ibmfl_module_location )
        from ibmfl.party.party import Party
        self.Party = Party(**kwargs)
        self.connection = self.Party.connection

    def start(self):
        self.Party.start()

    def isStopped(self):
        return self.Party.connection.stopped
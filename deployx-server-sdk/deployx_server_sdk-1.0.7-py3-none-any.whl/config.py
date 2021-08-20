import logging

class Config:

    def __init__(self, 
                 sdk_key=None,
                 debug=False):
        self.sdk_key = sdk_key
        self.offline = False
        self.debug = debug
        self.api_url = 'api.deploy-x.com' if not debug else 'localhost'
        self.api_port = '80' if not debug else '8000'

        self.available_params_list = ['sdk_key']

    @classmethod
    def default(cls):
        return cls

    def set_config(self, config):
        """
        * Install config parametrs from available param list
        """
        if isinstance(config, Config):
            return self._set_instance_config(config)

        if isinstance(config, dict):
            return self._set_dict_config(config)

        raise AttributeError('Config must be a dictionary or a Config() type. Example of dict attributes: { UNIQUE_IDENTIFIER: "some hash", username: "Josh Bold" }.\n'
                             ' Config() instance you can import from dxclient.config.')
    
    def _set_instance_config(self, config):
        logging.info('Install config via Config() instance.')
        for attr in self.available_params_list:
            if hasattr(config, attr) and len(getattr(config, attr)):
                setattr(self, attr, getattr(config, attr))
        return self

    def _set_dict_config(self, config):
        logging.info('Install config from config dictionary.')
        for key in config:
            if hasattr(self, key) and isinstance(config[key], str) and key in self.available_params_list:
                if len(config[key]) > 0:
                    setattr(self, key, config[key])
        return self

        
    def set_sdk_key(self, key):
        if isinstance(key, str):
            self.sdk_key = key
            return
        raise AttributeError('SDK_KEY must be str() type.')



import sys
import os
import json
from platform import python_version

try:
    from dotenv import load_dotenv
except ImportError:
    if(python_version() >= '3.0'):
        sys.exit("You need dotenv! install it from http://pypi.python.org/pypi/python-dotenv or run python3 -m pip install python-dotenv.")
    else:
        sys.exit("You need dotenv! install it from http://pypi.python.org/pypi/python-dotenv or run python -m pip install python-dotenv.")

try:
    import requests as request
except ImportError:
    if(python_version() >= '3.0'):
        sys.exit("You need dotenv! install it from http://pypi.python.org/pypi/requests or run python3 -m pip install requests.")
    else:
        sys.exit("You need requests install it from http://pypi.python.org/pypi/requests or run python -m pip install requests")

class RemoteConfig:

    config = {}
    config['BACKEND_URL'] = 'https://svmon.eudat.eu/api/serviceComponent/jsonreport'
    config['REMOTE_CONFIG_URL'] = 'https://svmon.eudat.eu/api/remoteConfig/'
    config['DEBUG_MODE'] = False

    def __init__(self):
        load_dotenv()
        self.loadEnvVars()

    def loadRemoteConfig(self):
        try:
            headers = {}
            headers['Content-Type'] = 'application/json'
            url = self.config['REMOTE_CONFIG_URL']
            apiToken = self.getUserApiToken()

            if(apiToken):
                headers['Authorization'] = 'Bearer ' + apiToken
                url = url + 'user'
            response = request.get(url, headers=headers)
            responseBody = response.json()

            if(response.status_code != 200):
                if(self.config['DEBUG_MODE']):
                    print('Recover of remote config FAILED ', response.status_code)
                    print('Failed to load remote config, using default env vars...')
                return False
            else:
                if(self.config['DEBUG_MODE']):
                    print('Recover of remote config finished with code ', response.status_code)

            if('environments' in responseBody):
                environments = responseBody["environments"]
                if('backendUrl' in environments):
                    self.config["BACKEND_URL"] = environments["backendUrl"]
                if('debugMode' in environments):
                    self.config["DEBUG_MODE"] = environments["debugMode"]
            return True

        except request.exceptions.RequestException as e:
            if(self.config['DEBUG_MODE']):
                print('Failed to load remote config, using default env vars...')
                print(e)
            return False

    def getUserApiToken(self):
        from . import services
        cwd = os.path.dirname(services.__file__)
        apiToken = None
        filename = os.environ.get('TOKEN_PATH', cwd + "/token.json")
        if os.path.exists(filename) == False:
            return None
        if os.access(filename, os.R_OK) == False:
            return None
        with open(filename, 'r') as f:
            load_dict = json.load(f)
            if 'token' in load_dict and load_dict.get('token') != '':
                apiToken = load_dict.get('token')
            else:
                return None
        self.config['TOKEN'] = apiToken
        return apiToken

    def loadEnvVars(self):
        remoteEnvVars = self.loadRemoteConfig()
        if(remoteEnvVars and self.config['DEBUG_MODE']):
            print("Remote environment variables loaded: ")
            print(self.config)
        else:
            backendUrl = os.environ.get('BACKEND_URL', self.config['BACKEND_URL'])
            self.config['BACKEND_URL'] = backendUrl
            debugMode = os.environ.get('DEBUG_MODE', self.config['DEBUG_MODE'])
            self.config['DEBUG_MODE'] = debugMode
        return self.config

    def getConfig(self):
        return self.config

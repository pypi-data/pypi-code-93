import xepmts_server
from werkzeug.wsgi import pop_path_info, peek_path_info
from flask import request

import json
import time

REFRESH_PERIOD = 3600


def clean_dict(d):
    return {k1: {k2:v2 for k2,v2 in v1.items() if is_jsonable(v2)} for k1,v1 in d.items()}

def add_server_spec_endpoint(app):
    @app.route(f'/{app.config["API_VERSION"]}/server-spec')
    def server_spec():
        spec = {
            'base_url': f'{request.base_url}/{app.config["API_VERSION"]}/', 
            'endpoints': clean_dict(app.config['DOMAIN'])
        }
        return spec
    return app
    
class PathMakerDispatcher:
    def __init__(self, base_app, static_apps, app_configs):
        self.base_app = base_app
        self.static_apps = static_apps
        self.app_configs = app_configs
        self.dynamic_apps = {v: (time.time(), self.make_app(v)) for v in app_configs}
    
    def make_app(self, v):
        return xepmts_server.get_server(v, **self.app_configs[v])

    def get_app(self, v):
        if v in self.static_apps:
            return self.static_apps[v]

        if v in self.dynamic_apps:
            t,app = self.dynamic_apps[v]
            if REFRESH_PERIOD<(time.time()-t):
                self.dynamic_apps[v] = t,app = time.time(), self.make_app(v)
            return app
        return self.base_app

    def __call__(self, environ, start_response):
        app = self.get_app(peek_path_info(environ))
        return app(environ, start_response)

class PathDispatcher:

    def __init__(self, base_app, app_dict):
        self.base_app = base_app
        self.apps = app_dict
        

    def __call__(self, environ, start_response):
        app = self.apps.get(peek_path_info(environ), self.base_app)
        return app(environ, start_response)

def is_jsonable(x):
    try:
        json.dumps(x)
        return True
    except (TypeError, OverflowError):
        return False

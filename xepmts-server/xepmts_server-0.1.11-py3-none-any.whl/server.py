import os

from flask import Flask


from threading import Lock
from werkzeug.wsgi import pop_path_info, peek_path_info
from werkzeug.serving import run_simple as _run_simple

from .v1.app import make_app as make_v1_app
from .v1.auth import XenonTokenAuth
from .v2.app import make_app as make_v2_app
from .admin.app import make_app as make_admin_app

from .utils import PathDispatcher, PathMakerDispatcher, add_server_spec_endpoint
import xepmts_server
from eve_jwt import JWTAuth

APP_MAKERS = {
    'v1': lambda: make_v1_app(auth=XenonTokenAuth, swagger=True),
    'v2': lambda: make_v2_app(auth=JWTAuth, swagger=True)
}

PRODUCTION_CONFIGS = {
    'v1': dict(auth=XenonTokenAuth, swagger=True),
    'v2': dict(auth=JWTAuth, swagger=True)
}

DEBUG_CONFIGS = {
    'v1': dict(swagger=True),
    'v2': dict(swagger=True),
}

def create_app():
    from eve_jwt import JWTAuth
    from flask_swagger_ui import get_swaggerui_blueprint
    
    
    v1 = make_v1_app(auth=XenonTokenAuth, swagger=True)
    v2 = make_v2_app(auth=JWTAuth, swagger=True)
    
    app_versions = {
        "v1": v1, 
        "v2": v2,
        }

    app = Flask(__name__)
    
    # @app.route("/")
    # def hello():
    #     return "You have reached the PMT db."

    app.config['SWAGGER_INFO'] = {
            'title': 'XENON PMT API',
            'version': '1.0',
            'description': 'API for the XENON PMT database',
            'termsOfService': 'https://opensource.org/ToS',
            'contact': {
                'name': 'Yossi Mosbacher',
                'url': 'https://pmts.xenonnt.org',
                "email": "joe.mosbacher@gmail.com"
            },

            'license': {
                'name': 'BSD',
                'url': 'https://github.com/nicolaiarocci/eve-swagger/blob/master/LICENSE',
            
            },
            'schemes': ['http', 'https'],

        }
    config = {
        'app_name': "PMT Database API",
        "urls": [{"name": f"Xenon PMT Database {v.capitalize()}", "url": f"/{v}/api-docs" } for v in app_versions]
    }
    API_URL = '/v2/api-docs'
    SWAGGER_URL = ''
    SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config=config,
    )
    app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)
    application = PathDispatcher(app,
                         app_versions)

    return application

def settings_dict(module):
    return {k: getattr(module, k) for k in dir(module) if k.isupper()}

def make_app(debug=False, overides={}, export_metrics=True, healthcheck=True):
    from eve_jwt import JWTAuth
    from flask_swagger_ui import get_swaggerui_blueprint
    
    # if versions is None:
    #     versions = xepmts_server.VERSIONS
    admin_auth = JWTAuth
    if debug:
        admin_auth = None
    admin = make_admin_app(auth=admin_auth, swagger=True)
    static_apps = {"admin": admin}
    if debug:
        configs = DEBUG_CONFIGS
    else:
        configs = PRODUCTION_CONFIGS
    
    app_configs = {}
    with admin.app_context():
        for version, config_kwargs in configs.items():
            kwargs = dict(config_kwargs)
            kwargs.update(overides)
            vmodule = getattr(xepmts_server, version)
            settings = kwargs.get('settings', settings_dict(vmodule.settings))
       
            endpoints = admin.data.driver.db[f'{version}_endpoints'].find()
            endpoints = {endpoint.pop('name'): endpoint for endpoint in endpoints}
            if endpoints:
                print(f'endpoints for version {version} taken from database.')
                settings['DOMAIN'] = endpoints
            kwargs['settings'] = settings
            kwargs['healthcheck'] = healthcheck
            kwargs['export_metrics'] = export_metrics
            app_configs[version] = kwargs
 

    app = Flask(__name__)

    app.config['SWAGGER_INFO'] = {
            'title': 'XENON PMT API',
            'version': '1.0',
            'description': 'API for the XENON PMT database',
            'termsOfService': 'https://opensource.org/ToS',
            'contact': {
                'name': 'Yossi Mosbacher',
                'url': 'https://pmts.xenonnt.org',
                "email": "joe.mosbacher@gmail.com"
            },

            'license': {
                'name': 'BSD',
                'url': 'https://github.com/nicolaiarocci/eve-swagger/blob/master/LICENSE',
            
            },
            'schemes': ['http', 'https'],

        }
    swagger_config = {
        'app_name': "PMT Database API",
        "urls": [{"name": f"Xenon PMT Database {v.capitalize()}", "url": f"/{v}/api-docs" } for v in list(app_configs)+list(static_apps)]
    }
    API_URL = '/v2/api-docs'
    SWAGGER_URL = os.getenv('SWAGGER_URL_PREFIX', '')
    SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config=swagger_config,
    )
    app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)
    if export_metrics:
        from prometheus_flask_exporter import PrometheusMetrics
        PrometheusMetrics(app)

    application = PathMakerDispatcher(app,
                          static_apps=static_apps,
                          app_configs=app_configs)
    return application


def run_simple(address='0.0.0.0', port=5000, debug=True, reload=True, evalex=True):
    app = make_app(debug=debug)
    _run_simple(address, port, app,
                use_reloader=debug, use_debugger=reload, use_evalex=evalex)

if __name__ == '__main__':
    run_simple()
    
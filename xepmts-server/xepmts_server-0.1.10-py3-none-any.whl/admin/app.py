
from eve import Eve
from werkzeug.serving import run_simple as _run_simple

from xepmts_server.admin import settings as settings
from xepmts_server.utils import clean_dict

settings_file = settings.__file__

def make_app(settings=settings_file, auth=None, app=None,
             swagger=False, fs_store=False,
             export_metrics=False, **kwargs):

    if app is None:
        from eve import Eve
        app = Eve(settings=settings, auth=auth, **kwargs)

    if swagger:
        # from eve_swagger import swagger as swagger_blueprint
        from eve_swagger import get_swagger_blueprint
        
        swagger_blueprint = get_swagger_blueprint()
        app.register_blueprint(swagger_blueprint, url_prefix=f'/{app.config["API_VERSION"]}')
        app.config['SWAGGER_INFO'] = {
            'title': 'XENON PMT API ENDPOINTS',
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

    @app.route(f'/{app.config["API_VERSION"]}/endpoints')
    def endpoints():
        return clean_dict(app.config['DOMAIN'])

    if export_metrics:
        from prometheus_flask_exporter import PrometheusMetrics
        PrometheusMetrics(app, path=f'/{app.config["API_VERSION"]}/metrics')

    return app

def run_simple(address='0.0.0.0', port=5000, debug=True, reload=True, evalex=True):
    app = make_app()
    _run_simple(address, port, app,
                use_reloader=debug, use_debugger=reload, use_evalex=evalex)


if __name__ == '__main__':
    run_simple()
    
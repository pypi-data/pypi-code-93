from microservice_template_core.settings import FlaskConfig, ServiceConfig, DbConfig
from flask import Flask, Blueprint
from flask_cors import CORS
from prometheus_client import make_wsgi_app
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from prometheus_flask_exporter import PrometheusMetrics
from flask_restx.apidoc import apidoc


class Core:
    def __init__(self):
        self.config = ServiceConfig.configuration
        self.namespaces = self.config.get('namespaces', [])
        self.blueprint = None
        self.register_namespaces()
        self.app = self.create_flask_app()
        self.ma = None
        if DbConfig.USE_DB:
            self.connect_db()
        if FlaskConfig.FLASK_JWT:
            self.add_authorization()

    def run(self):
        self.app.run(debug=FlaskConfig.FLASK_DEBUG,
                     port=ServiceConfig.SERVICE_PORT,
                     host=ServiceConfig.SERVER_NAME,
                     threaded=FlaskConfig.FLASK_THREADED
                     )

    def register_namespaces(self):
        from microservice_template_core.tools.flask_restplus import api
        apidoc.url_prefix = ServiceConfig.URL_PREFIX
        self.blueprint = Blueprint('api', __name__, url_prefix=ServiceConfig.URL_PREFIX)
        api.init_app(self.blueprint)
        from microservice_template_core.api.namespaces.core_endpoints import ns as core_endpoints
        default_namespaces = [core_endpoints]

        for namespace in default_namespaces + self.namespaces:
            api.add_namespace(namespace)

    def connect_db(self):
        from microservice_template_core.tools.db import db
        db.init_app(self.app)
        db.app = self.app
        db.create_all()

    def add_authorization(self):
        from flask_jwt_extended import JWTManager
        self.app.config['JWT_SECRET_KEY'] = FlaskConfig.JWT_SECRET_KEY
        self.app.config['JWT_DECODE_ALGORITHMS'] = FlaskConfig.JWT_DECODE_ALGORITHMS
        self.app.config['JWT_IDENTITY_CLAIM'] = FlaskConfig.JWT_IDENTITY_CLAIM
        self.app.config['JWT_USER_CLAIMS'] = FlaskConfig.JWT_USER_CLAIMS
        self.app.config['PROPAGATE_EXCEPTIONS'] = FlaskConfig.PROPAGATE_EXCEPTIONS
        JWTManager(self.app)

    def create_flask_app(self):
        app = Flask(__name__)
        metrics = PrometheusMetrics(app)
        CORS(app)
        app.register_blueprint(self.blueprint)
        app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {'/metrics': make_wsgi_app()})
        app.config['SQLALCHEMY_DATABASE_URI'] = DbConfig.SQLALCHEMY_DATABASE_URI
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = DbConfig.SQLALCHEMY_TRACK_MODIFICATIONS
        app.config['SQLALCHEMY_POOL_RECYCLE'] = DbConfig.SQLALCHEMY_POOL_RECYCLE
        return app

    def configure_opentelemetry_client(self):
        pass

    def configure_prometheus_metrics(self):
        pass

    def configure_db(self):
        pass


def main():
    microservice_template_core = Core()
    microservice_template_core.run()


if __name__ == '__main__':
    main()

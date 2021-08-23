import pytest
from flask import Flask
from flask import jsonify
from flask.testing import FlaskClient

from jsm_user_services.flask import middleware
from jsm_user_services.support.local_threading_utils import get_from_local_threading


@pytest.fixture(autouse=True)
def flask_app() -> Flask:
    app = Flask(__name__)

    app.config.setdefault("USER_API_HOST", "http://flask-app")
    middleware.JsmJwtService(app)

    @app.route("/authorization-token", methods=["GET"])
    def retrieve_authorization_token():
        return jsonify({"auth_token": get_from_local_threading("authorization_token")})

    @app.route("/my-ip", methods=["GET"])
    def retrieve_user_ip():
        return jsonify({"ip": get_from_local_threading("user_ip")})

    @app.route("/session-id", methods=["GET"])
    def retrieve_user_session_id():
        return jsonify({"session_id": get_from_local_threading("user_session_id")})

    return app


@pytest.fixture
def flask_test_client(flask_app: Flask) -> FlaskClient:
    flask_app.testing = True
    return flask_app.test_client()

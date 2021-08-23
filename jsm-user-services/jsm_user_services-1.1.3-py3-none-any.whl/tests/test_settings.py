import pytest
from django.conf import LazySettings as DjangoSettings
from flask import Flask
from flask.config import Config as FlaskSettings
from pytest_mock import MockFixture

from jsm_user_services import settings
from jsm_user_services.exception import ApplicationSettingsNotFound
from jsm_user_services.settings import get_setting_from_app


@pytest.fixture
def flask_app():
    app = Flask(__name__)

    app.config["USER_API_HOST"] = "http://flask-app"

    with app.app_context():
        yield


@pytest.fixture
def no_django(mocker: MockFixture):
    mocker.patch("jsm_user_services.settings.get_django_settings", return_value=None)


@pytest.fixture
def no_flask(mocker: MockFixture):
    mocker.patch("jsm_user_services.settings.get_flask_settings", return_value=None)


def test_should_correctly_retrieve_django_settings():
    django_settings = settings.get_django_settings()

    assert isinstance(django_settings, DjangoSettings)
    assert django_settings.USER_API_HOST == "http://ishtar-gate.dev.juntossomosmaisi.com.br/api/v1"


def test_should_correctly_retrieve_flask_settings(flask_app: None):
    flask_settings = settings.get_flask_settings()

    assert isinstance(flask_settings, FlaskSettings)
    assert flask_settings.get("USER_API_HOST") == "http://flask-app"


def test_should_correctly_retrieve_setting_from_flask_app(flask_app: None, no_django: None):
    assert get_setting_from_app("USER_API_HOST") == "http://flask-app"


def test_should_correctly_retrieve_settings_from_django_app(no_flask: None):
    assert get_setting_from_app("USER_API_HOST") == "http://ishtar-gate.dev.juntossomosmaisi.com.br/api/v1"


def test_should_raise_exception_when_application_settings_isnt_found(no_django: None):
    with pytest.raises(ApplicationSettingsNotFound):
        get_setting_from_app("USER_API_HOST")

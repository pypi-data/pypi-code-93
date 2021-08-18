""" Defines the configuration for Soil """
from typing import Optional, NamedTuple
import logging
import time
import os
from os import getenv
import json
import requests
import jwt

# TODO add windows support

# pylint: disable=invalid-name
env = getenv("PY_ENV", "development")


def _refresh_token(auth_host: str, refresh_token: str) -> str:
    url = auth_host + "/api/jwt/refresh"
    response = requests.post(url, json={"refreshToken": refresh_token})
    if response.status_code != 200:
        raise ValueError("Invalid refresh token please run soil login again.")
    return json.loads(response.text)["token"]


def get_soil_root(relpath: str) -> Optional[str]:
    """Checks if the current dir is under a soil environment and returns its root. Returns None otherwise."""
    path = os.path.abspath(relpath) + "/"
    while path != "/":
        path, _ = os.path.split(path)
        if "soil.yml" in os.listdir(path):
            return path
    return None


project_root = get_soil_root(".")
SOIL_URL = ""
if env != "test":
    try:
        if project_root is None:
            raise FileNotFoundError("Project root not found.")
        with open(project_root + "/soil.conf") as conf_file:
            CONF = json.loads(conf_file.read())
            SOIL_URL = CONF["soil_url"]
        logging.info(
            "Loaded config from %s using app_id %s",
            project_root + "/soil.conf",
            CONF["auth_app_id"],
        )
    except FileNotFoundError:
        try:
            with open(getenv("HOME", "") + "/.soil/soil.conf") as conf_file:
                CONF = json.loads(conf_file.read())
                SOIL_URL = CONF["soil_url"]
            logging.warning(
                "Loaded config from %s using app_id %s. It is recommended to have a soil.conf file at the root of the project.", # NOQA pylint:disable=line-too-long
                getenv("HOME", "") + "/.soil/soil.conf",
                CONF["auth_app_id"],
            )

        except FileNotFoundError:
            logging.error(
                "~/.soil/soil.conf file not found. Please run soil configure."
            )
else:
    SOIL_URL = "http://test_host.test"

TOKEN = ""  # nosec

if env != "test":
    try:
        with open(
            getenv("HOME", "") + "/.soil/" + CONF["auth_app_id"] + "/soil.env"
        ) as env_file:
            ENV = json.loads(env_file.read())
            TOKEN = _refresh_token(CONF["auth_url"], ENV["auth"]["refreshToken"])
    except FileNotFoundError:
        logging.warning(
            "~/.soil/%s/soil.env file not found. Using ~/.soil/soil.env instead. It is recommended to run soil login.",
            CONF["auth_app_id"],
        )
        try:
            with open(getenv("HOME", "") + "/.soil/soil.env") as env_file:
                ENV = json.loads(env_file.read())
                TOKEN = _refresh_token(CONF["auth_url"], ENV["auth"]["refreshToken"])
        except FileNotFoundError:
            logging.error("~/.soil/soil.env file not found. Please run soil login.")
else:
    TOKEN = "test_token"  # nosec

DEFAULT_CONFIG = {
    "host": getenv("SOIL_HOST", SOIL_URL),
    "token": getenv("SOIL_TOKEN", TOKEN),
}

if env != "test":
    decoded_token = jwt.decode(TOKEN, options={"verify_signature": False})
    conf_app_id = CONF["auth_app_id"].strip()
    token_app_id = decoded_token["applicationId"]

    if token_app_id != conf_app_id:
        raise Exception(
            "Application Id for the project config "
            + "{} does not coincide with the token application id {}.\n".format(
                conf_app_id, token_app_id
            )
            + "Please, run 'soil login' again."
        )


class SoilConfiguration(NamedTuple):
    """Soil configuration class"""

    host: Optional[str]
    token: Optional[str]

    def __getattribute__(self, name: str) -> str:
        """Refresh the token if necessary before accessing it."""
        # pylint:disable=global-statement
        global TOKEN

        if name != "token":
            return object.__getattribute__(self, name)

        if env == "test":
            return TOKEN

        # Min nummber of seconds before expire that will trigger a refresh.
        min_delta = 10

        exp = jwt.decode(TOKEN, options={"verify_signature": False})["exp"]
        if exp - time.time() < min_delta:
            TOKEN = _refresh_token(CONF["auth_url"], ENV["auth"]["refreshToken"])
        return TOKEN


GLOBAL_CONFIG = SoilConfiguration(**DEFAULT_CONFIG)


# Not used for now
# def config(token: Optional[str] = None, host: Optional[str] = None) -> SoilConfiguration:
#     ''' Set the Soil's configuration '''
#     global GLOBAL_CONFIG  # pylint: disable=global-statement
#     new_config = SoilConfiguration(token=token, host=host)
#     GLOBAL_CONFIG = SoilConfiguration(**{**GLOBAL_CONFIG._asdict(), **new_config._asdict()})
#     return GLOBAL_CONFIG

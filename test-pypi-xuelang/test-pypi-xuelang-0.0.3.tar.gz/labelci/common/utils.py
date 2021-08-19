import sys
import os
import requests
from datetime import datetime

from labelci.common.exception.labelci_sdk_exception import (
    AuthenticationException,
    AuthorizationException,
    BadGatewayException,
    BadRequestException,
    GatewayTimeoutException,
    LockedException,
    OverLimitException,
    ResourceNotFoundException,
    ServerException,
    UnexpectedStatusCodeException,
    InvalidTokenException,
)


def check_response_status(response: requests.Response):
    """Check response status and throw corresponding exception on failure."""
    code = response.status_code
    if code >= 200 and code < 300:
        return

    try:
        message = response.json()["description"]
    except Exception:
        message = " "

    if code == 400:
        if message != " ":
            sys.exit("Error: {message}")
        raise BadRequestException(message)
    elif response.status_code == 401:
        raise AuthenticationException
    elif response.status_code == 403:
        raise AuthorizationException(message)
    elif response.status_code == 404:
        if message != " ":
            raise ResourceNotFoundException(message)
        raise ResourceNotFoundException
    elif response.status_code == 423:
        raise LockedException
    elif response.status_code == 429:
        raise OverLimitException
    elif response.status_code == 502:
        raise BadGatewayException
    elif response.status_code == 504:
        raise GatewayTimeoutException
    elif 500 <= response.status_code < 600:
        raise ServerException("Server under maintenance, try again later.")
    else:
        message = f"An error occurred. Server response: {response.status_code}"
        raise UnexpectedStatusCodeException(message)


def save_file(data, export_type, save_path):
    """save file
    """
    if not os.path.exists(save_path):
        os.mkdir(save_path)
    with open(save_path) as f:
        f.write(data)

    return "ok"


def project_exists():
    pass


def get_filename(project_id):
    t = datetime.now().isoformat(sep="-")
    return "-".join(["project_id", str(project_id), t])


def dir_exists(path):
    if not os.path.exists(path):
        os.mkdir(path)

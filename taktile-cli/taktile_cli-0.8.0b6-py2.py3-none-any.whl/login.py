from functools import wraps

import requests
from pydantic.types import UUID4

from tktl.core.config import settings
from tktl.core.loggers import LOG
from tktl.core.managers.auth import AuthConfigManager
from tktl.core.strings import CLIStrings, HeaderStrings


def login(api_key=None):
    """

    Parameters
    ----------
    api_key

    Returns
    -------

    """
    if api_key is None:
        LOG.error("Authentication failed: no key provided")
        return False
    try:
        UUID4(api_key)
    except ValueError:
        LOG.error("Authentication failed: Key format is invalid")
        return False
    AuthConfigManager.set_api_key(api_key)
    return True


def set_api_key(api_key):
    AuthConfigManager.set_api_key(api_key=api_key)
    path = (
        f"{AuthConfigManager.get_tktl_config_path()}/"
        f"{AuthConfigManager.SETTINGS.CONFIG_FILE_NAME}"
    )
    LOG.log(f"Successfully added your API Key to {path} You're ready to go!")
    return True


def logout():
    AuthConfigManager.clear_tktl_config()
    return True


def validate_key(suppress=False, api_key=None):
    if not api_key:
        api_key = AuthConfigManager.get_api_key()
    if not api_key:
        LOG.error(CLIStrings.AUTH_ERROR_MISSING_KEY)
        return False

    r = requests.get(
        f"{settings.TAKTILE_API_URL}{settings.API_V1_STR}/users/me",
        headers={"Accept": HeaderStrings.APPLICATION_JSON, "X-Api-Key": api_key},
    )
    try:
        r.raise_for_status()
    except requests.exceptions.RequestException:
        LOG.error(f'Request failed: {r.json()["detail"]}')
        return False

    if not suppress:
        LOG.log("Login successful!", color="green")
    return True


def validate_decorator(func):
    @wraps(func)
    def wrapped_validation(*args, **kwargs):
        if not validate_key(suppress=True):
            return
        return func(*args, **kwargs)

    return wrapped_validation

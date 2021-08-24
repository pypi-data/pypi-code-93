"""Baseten

    isort:skip_file
"""

__version__ = '0.1.0'

import logging
from collections import defaultdict

patched_modules = defaultdict(lambda: [])

from baseten.baseten_deployed_model import BasetenDeployedModel  # noqa: E402
from baseten.baseten_deployed_model import install_requirements, requirements_status  # noqa: E402, F401
from baseten.common.model_deployer import deploy_custom_model, deploy_model_object  # noqa: E402
from baseten.common.util import setup_logger  # noqa: E402
from baseten.common import settings  # noqa: E402


logger = logging.getLogger(__name__)
setup_logger('baseten', logging.INFO)
if settings.DEBUG:
    setup_logger('baseten', logging.DEBUG)
logger.debug(f'Starting the client with the server URL set to {settings.API_URL_BASE}')

# The Baseten model ID that either a) the user initialized baseten with, or b) was created when deploying a model.
working_model_id = None
deploy = deploy_model_object  # This allows the user to call baseten.deploy(model)
deploy_custom = deploy_custom_model  # This allows the user to call baseten.deploy_custom(...)


def set_log_level(level):
    setup_logger('baseten', level)


def init(baseten_model_id=None):
    """Initialize Baseten

    Args:
        baseten_model_id (str, optional): The BaseTen model id to initialize the client with.
        If not provided, a new Baseten model will be created at deploy() time.
    """
    global working_model_id
    working_model_id = baseten_model_id


def deployed_model_id(model_id: str) -> BasetenDeployedModel:
    """Returns a BasetenDeployedModel object for interacting with the model model_id.

    Args:
        model_id (str)

    Returns:
        BasetenDeployedModel
    """
    return BasetenDeployedModel(model_id=model_id)


def deployed_model_version_id(model_version_id: str) -> BasetenDeployedModel:
    """Returns a BasetenDeployedModel object for interacting with the model version model_version_id.

    Args:
        model_version_id (str)

    Returns:
        BasetenDeployedModel
    """
    return BasetenDeployedModel(model_version_id=model_version_id)


def login(api_key: str):
    """Set the API key for the client.

    Args:
        api_key (str)
    """
    settings.set_config_value('api', 'api_key', api_key)
    logger.info('API key set.')

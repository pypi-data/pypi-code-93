from flask import current_app as app
from flask import session
from inbotauth import azure, google
import logging

LOGGER = logging.getLogger(__name__)


def get_token_from_cache():
    LOGGER.info(session.get('login_type'))
    if session.get('login_type') == 'google':
        return google.get_token_from_cache()
    if session.get('login_type') == 'microsoft':
        return azure.get_token_from_cache(scope=app.config['MS_SCOPE'])['secret']
    return None

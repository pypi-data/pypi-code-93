import logging
from re import Pattern
from datetime import datetime, timedelta

from django.conf import settings

logger = logging.getLogger(__name__)


def get_cookie_equivalency(name=None, all_names=False):
    """
    Gets the equivalent cookie name.
    Used only to mask the cookies.
    """
    EQUIVALENCY = {
        'oidc_id_token_expiration': 'dn_oite',
        'oidc_access_token': 'dn_oat',
        'oidc_id_token': 'dn_oit',
        'oidc_states': 'dn_os',
        'oidc_login_next': 'dn_oln',
    }

    return EQUIVALENCY.get(name) if not all_names else EQUIVALENCY


def get_cookie_configuration():
    """
    Cookie configuration
    """
    expiration_datetime = \
            datetime.now() + timedelta(minutes=settings.AUTH_COOKIE_EXPIRATION_MINUTES)
    expires = expiration_datetime.strftime("%a, %d-%b-%Y %H:%M:%S GMT")

    return {
        'expires': expires,
        'domain': settings.AUTH_COOKIE_DOMAIN,
        'secure': settings.AUTH_COOKIE_SECURE,
        'httponly': settings.AUTH_COOKIE_HTTPONLY,
        'samesite': 'Strict'
    }


def generate_oidc_cookies(session, response):
    """
    Generates all the cookies needed on another clients to process the user
    """
    # This script only works if we save the access token in session
    if settings.OIDC_STORE_ACCESS_TOKEN:
        oidc_id_token_expiration = session.get('oidc_id_token_expiration', None)
        oidc_access_token = session.get('oidc_access_token', None)
        oidc_id_token = session.get('oidc_id_token', None)
        oidc_states = session.get('oidc_states', {})
        oidc_login_next = session.get('oidc_login_next', '')

        # We need these tree variables to login, if at least one is None or empty, then return
        if not all([oidc_id_token_expiration, oidc_access_token, oidc_id_token]):
            logger.debug("No valid token found, returning default response")
            return response

        # Extra kwargs used in set_cookie
        extra_data = get_cookie_configuration()

        # Setting the cookies...
        response.set_cookie(get_cookie_equivalency('oidc_id_token_expiration'), oidc_id_token_expiration, **extra_data)
        response.set_cookie(get_cookie_equivalency('oidc_access_token'), oidc_access_token, **extra_data)
        response.set_cookie(get_cookie_equivalency('oidc_login_next'), oidc_login_next, **extra_data)
        response.set_cookie(get_cookie_equivalency('oidc_id_token'), oidc_id_token, **extra_data)
        response.set_cookie(get_cookie_equivalency('oidc_states'), oidc_states, **extra_data)

    return response


def delete_oidc_cookies(response):
    """
    Deletes all the cookies (if exists) if the user is not logged in
    """
    extra_data = get_cookie_configuration()
    extra_data.pop('expires')
    extra_data.pop('secure')
    extra_data.pop('httponly')

    response.delete_cookie(get_cookie_equivalency('oidc_id_token_expiration'), **extra_data)
    response.delete_cookie(get_cookie_equivalency('oidc_access_token'), **extra_data)
    response.delete_cookie(get_cookie_equivalency('oidc_login_next'), **extra_data)
    response.delete_cookie(get_cookie_equivalency('oidc_id_token'), **extra_data)
    response.delete_cookie(get_cookie_equivalency('oidc_states'), **extra_data)
    response.delete_cookie('sessionid')

    return response

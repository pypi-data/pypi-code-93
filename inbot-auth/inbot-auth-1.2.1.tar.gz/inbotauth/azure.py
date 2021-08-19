import uuid
import requests
from flask import session, url_for
from flask import current_app as app
import msal
from typing import Dict


def load_cache():
    cache = msal.SerializableTokenCache()
    if session.get("token_cache"):
        cache.deserialize(session["token_cache"])
    return cache


def save_cache(cache):
    if cache.has_state_changed:
        session["token_cache"] = cache.serialize()


def build_msal_app(cache=None):
    return msal.ConfidentialClientApplication(app.config['MS_CLIENT_ID'],
                                              client_credential=app.config['MS_CLIENT_SECRET'],
                                              token_cache=cache)


def build_auth_url(scopes=None, state=None):
    redirect_uri = url_for("mscallback", _external=True)
    return build_msal_app().get_authorization_request_url(
        scopes or [],
        state=state or str(uuid.uuid4()),
        redirect_uri=redirect_uri)


def get_token_from_cache(scope=None):
    cache = load_cache()  # This web app maintains one cache per session
    if session.get("token_cache"):
        return cache.find("AccessToken")[0]
    cca = build_msal_app(cache=cache)
    accounts = cca.get_accounts()
    if accounts:  # So all account(s) belong to the current signed-in user
        result = cca.acquire_token_silent(scope, account=accounts[0])
        save_cache(cache)
        return result


def query_user_info(token) -> Dict:
    """
    query user info from oidc server with access token
    """
    return requests.get(  # Use token to call downstream service
        app.config['MS_USER_ENDPOINT'],
        headers={'Authorization': 'Bearer ' + token['secret']},
    ).json()


def get_user(token=None):
    if session.get("auth_user"):
        return session["auth_user"]
    else:
        # if the user is not in session cache, query the user info from OIDC server with the token,
        # and update the user info to local db
        user_info = query_user_info(token)
        user = app.config['PUT_USER_METHOD'](app, user_info)
        session["auth_user"] = user
        return user

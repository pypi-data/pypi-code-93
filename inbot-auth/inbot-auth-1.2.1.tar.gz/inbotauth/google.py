import uuid
import json
import requests
from flask import current_app as app
from flask import session, url_for
from oauthlib.oauth2 import WebApplicationClient

import logging
LOGGER = logging.getLogger(__name__)

def get_provider_cfg():
    return requests.get(app.config["GOOGLE_DISCOVERY_URL"]).json()


def get_client():
    return WebApplicationClient(app.config["GOOGLE_CLIENT_ID"])


def build_auth_url(scopes=None, state=None):
    # Find out what URL to hit for Google login
    google_provider_cfg = get_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]
    redirect_uri = url_for("gcallback", _external=True)
    # Use library to construct the request for Google login and provide
    # scopes that let you retrieve user's profile from Google
    return get_client().prepare_request_uri(
        authorization_endpoint,
        redirect_uri=redirect_uri,
        scope=scopes or [],
        state=state or str(uuid.uuid4()))


def get_token(request, code, client):
    client = get_client()
    # Find out what URL to hit to get tokens that allow you to ask for
    # things on behalf of a user
    google_provider_cfg = get_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]
    # Prepare and send a request to get tokens! Yay tokens!
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code)

    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(app.config["GOOGLE_CLIENT_ID"], app.config["GOOGLE_CLIENT_SECRET"]))

    # Parse the tokens!
    client.parse_request_body_response(json.dumps(token_response.json()))
    return client


def query_user_info(client):
    # Now that you have tokens (yay) let's find and hit the URL
    # from Google that gives you the user's profile information,
    # including their Google profile image and email
    userinfo_endpoint = get_provider_cfg()["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)
    return userinfo_response.json()


def get_token_from_cache():
    token_cache = session.get("token_cache")
    if token_cache is not None:
        return token_cache.get("access_token")

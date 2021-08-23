from __future__ import unicode_literals

import json
import logging
import os
import requests
import requests_oauthlib

from mopidy import httpclient, exceptions

from . import Extension, __version__

logger = logging.getLogger(__name__)

REQUIRED_SCOPES = ["read:libraries", "read:favorites", "read:playlists"]


class SessionWithUrlBase(requests.Session):
    # In Python 3 you could place `url_base` after `*args`, but not in Python 2.
    def __init__(self, url_base=None, *args, **kwargs):
        super(SessionWithUrlBase, self).__init__(*args, **kwargs)
        self.url_base = url_base

    def request(self, method, url, **kwargs):
        # Next line of code is here for example purposes only.
        # You really shouldn't just use string concatenation here,
        # take a look at urllib.parse.urljoin instead.
        if url.startswith("http://") or url.startswith("https://"):
            modified_url = url
        else:
            modified_url = self.url_base + url

        return super(SessionWithUrlBase, self).request(method, modified_url, **kwargs)


class OAuth2Session(SessionWithUrlBase, requests_oauthlib.OAuth2Session):
    pass


def get_requests_session(url, proxy_config, user_agent, base_cls, **kwargs):
    if not url.endswith("/"):
        url += "/"
    url += "api/v1/"

    proxy = httpclient.format_proxy(proxy_config)
    full_user_agent = httpclient.format_user_agent(user_agent)

    session = base_cls(url_base=url, **kwargs)
    session.proxies.update({"http": proxy, "https": proxy})
    session.headers.update({"user-agent": full_user_agent})

    return session


def login_legacy(session, username, password):
    if not username:
        return
    response = session.post("token/", {"username": username, "password": password})
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        raise exceptions.BackendError("Authentication failed for user %s" % (username,))
    token = response.json()["token"]
    session.headers.update({"Authorization": "JWT %s" % (token,)})
    return token


class APIClient(object):
    def __init__(self, config):
        self.config = config
        self.jwt_token = None
        self.oauth_token = get_token(config)
        if self.use_oauth:
            self.session = get_requests_session(
                config["funkwhale"]["url"],
                proxy_config=config["proxy"],
                user_agent="%s/%s" % (Extension.dist_name, __version__),
                base_cls=OAuth2Session,
                client_id=self.config["funkwhale"]["client_id"],
                token=self.oauth_token,
                auto_refresh_url=config["funkwhale"]["url"]
                + config["funkwhale"].get("token_endpoint")
                or "/api/v1/oauth/token/",
                auto_refresh_kwargs={
                    "client_id": self.config["funkwhale"]["client_id"],
                    "client_secret": self.config["funkwhale"]["client_secret"],
                },
                token_updater=self.refresh_token,
            )
        else:
            self.session = get_requests_session(
                config["funkwhale"]["url"],
                proxy_config=config["proxy"],
                user_agent="%s/%s" % (Extension.dist_name, __version__),
                base_cls=SessionWithUrlBase,
            )
            self.username = self.config["funkwhale"]["username"]
        self.session.verify = config["funkwhale"].get("verify_cert", True)

    @property
    def use_oauth(self):
        return self.config["funkwhale"]["client_id"] and self.oauth_token

    def refresh_token(self, token):
        self.oauth_token = token
        set_token(token, self.config)

    def login(self):
        self.username = self.config["funkwhale"]["username"]
        if self.username:
            self.jwt_token = login_legacy(
                self.session,
                self.config["funkwhale"]["username"],
                self.config["funkwhale"]["password"],
            )
        else:
            self.jwt_token = None

    def search(self, query):
        response = self.session.get("search", params={"query": query})
        response.raise_for_status()
        return response.json()

    def get_track(self, id):
        response = self.session.get("tracks/{}/".format(id))
        response.raise_for_status()
        return response.json()

    def list_tracks(self, filters):
        response = self.session.get("tracks/", params=filters)
        response.raise_for_status()
        return response.json()

    def list_artists(self, filters):
        response = self.session.get("artists/", params=filters)
        response.raise_for_status()
        return response.json()

    def list_albums(self, filters):
        response = self.session.get("albums/", params=filters)
        response.raise_for_status()
        return response.json()

    def list_libraries(self, filters):
        response = self.session.get("libraries/", params=filters)
        response.raise_for_status()
        return response.json()

    def load_all(self, first_page, max=0):
        for i in first_page["results"]:
            yield i

        next_page = first_page.get("next")
        counter = 0
        while next_page:
            logger.info("Fetching next page of result at url: %s", next_page)
            response = self.session.get(next_page)
            response.raise_for_status()
            payload = response.json()
            for i in payload["results"]:
                yield i
            counter += 1
            next_page = payload.get("next")
            if max and counter >= max:
                next_page = None


def get_token(config):
    import mopidy_funkwhale

    data_dir = mopidy_funkwhale.Extension.get_data_dir(config)
    try:
        with open(os.path.join(data_dir, "token"), "r") as f:
            raw = f.read()
    except IOError:
        return None
    try:
        return json.loads(raw)
    except (TypeError, ValueError):
        logger.error("Cannot decode token data, you may need to relogin")


def set_token(token_data, config):
    import mopidy_funkwhale

    data_dir = mopidy_funkwhale.Extension.get_data_dir(config)
    print(data_dir)
    content = json.dumps(token_data)
    with open(os.path.join(data_dir, "token"), "w") as f:
        f.write(content)

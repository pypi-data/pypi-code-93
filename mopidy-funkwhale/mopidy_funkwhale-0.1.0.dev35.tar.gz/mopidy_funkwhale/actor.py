from __future__ import unicode_literals

import logging

from mopidy import backend

import pykka

from . import client
from . import library


logger = logging.getLogger(__name__)


class FunkwhaleBackend(pykka.ThreadingActor, backend.Backend):
    def __init__(self, config, audio):
        super(FunkwhaleBackend, self).__init__()
        self.config = config
        self.client = client.APIClient(config)
        self.library = library.FunkwhaleLibraryProvider(backend=self)
        self.playback = FunkwhalePlaybackProvider(audio=audio, backend=self)

        self.uri_schemes = ["funkwhale", "fw"]

    def on_start(self):
        if self.config["funkwhale"]["client_id"]:
            logger.info('Using OAuth2 connection"')
        elif self.client.username is not None:
            self.client.login()
            logger.info(
                'Logged in to Funkwhale as "%s" on "%s"',
                self.client.username,
                self.config["funkwhale"]["url"],
            )
        else:
            logger.info('Using "%s" anonymously', self.config["funkwhale"]["url"])


class FunkwhalePlaybackProvider(backend.PlaybackProvider):
    def translate_uri(self, uri):
        _, id = library.parse_uri(uri)
        track = self.backend.client.get_track(id)

        if track is None:
            return None
        url = track["listen_url"]

        if url.startswith("/"):
            url = self.backend.config["funkwhale"]["url"] + url
        if self.backend.client.use_oauth:
            url += "?token=" + self.backend.client.oauth_token["access_token"]

        elif self.backend.client.jwt_token:
            url += "?jwt=" + self.backend.client.jwt_token
        return url

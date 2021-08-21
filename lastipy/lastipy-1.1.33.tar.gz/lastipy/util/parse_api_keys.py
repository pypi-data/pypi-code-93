from configparser import ConfigParser


class ApiKeysParser:
    def __init__(self, file):
        self._extract_keys(file)

    def _extract_keys(self, file):
        config_parser = ConfigParser()
        config_parser.read(file.name)
        self.lastfm_api_key = config_parser["LastFM"]["API"]
        spotify_section = "Spotify"
        self.spotify_client_id_key = config_parser[spotify_section]["CLIENT_ID"]
        self.spotify_client_secret_key = config_parser[spotify_section]["CLIENT_SECRET"]

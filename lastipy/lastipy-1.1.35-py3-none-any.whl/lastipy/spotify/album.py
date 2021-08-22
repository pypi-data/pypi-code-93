class SpotifyAlbum:
    """Represents a Spotify "album". This is slightly confusing in that there are different "types" of albums: albums, and singles."""

    def __init__(
        self, name, artist, album_type, spotify_id, release_date_precision, release_date
    ):
        self.name = name
        self.artist = artist
        self.album_type = album_type
        self.spotify_id = spotify_id
        self.release_date_precision = release_date_precision
        self.release_date = release_date

    def __eq__(self, other):
        return (
            isinstance(other, SpotifyAlbum)
            and self.name == other.name
            and self.artist == other.artist
            and self.album_type == other.album_type
            and self.spotify_id == other.spotify_id
            and self.release_date_precision == self.release_date_precision
            and self.release_date == self.release_date
        )

    def __repr__(self):
        return str(self.__dict__)


SINGLE_ALBUM_TYPE = "single"
ALBUM_ALBUM_TYPE = "album"

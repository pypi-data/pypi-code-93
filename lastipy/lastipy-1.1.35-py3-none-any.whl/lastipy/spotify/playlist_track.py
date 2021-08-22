from lastipy.track import Track


class PlaylistTrack(Track):
    """Represents a Spotify track that exists in a playlist"""

    def __init__(self, track_name, artist, spotify_id, added_at):
        self.track_name = track_name
        self.artist = artist
        self.spotify_id = spotify_id
        self.added_at = added_at

    def __eq__(self, other):
        return (
            isinstance(other, Track)
            and self.track_name == other.track_name
            and self.artist == other.artist
            and self.spotify_id == other.spotify_id
            and self.added_at == other.added_at
        )

    def __repr__(self):
        return str(self.__dict__)

class ScrobbledArtist:
    """Represents an artist that has been scrobbled (ie: exists in the user's Last.fm library)"""

    def __init__(self, artist_name, playcount):
        self.artist_name = artist_name
        self.playcount = playcount

    def __eq__(self, other):
        return (
            isinstance(other, ScrobbledArtist)
            and self.artist_name == other.artist_name
            and self.playcount == other.playcount
        )

    def __repr__(self):
        return str(self.__dict__)

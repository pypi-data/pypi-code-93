from lastipy.track import Track


class TopTrack(Track):
    """Represents a top track that a user has scrobbled, with an associated playcount"""

    def __init__(self, track_name, artist, playcount):
        super().__init__(track_name, artist)
        self.playcount = playcount

    def __eq__(self, other):
        return (
            isinstance(other, TopTrack)
            and self.track_name == other.track_name
            and self.artist == other.artist
            and self.playcount == other.playcount
        )

    def __hash__(self):
        return hash((self.track_name, self.artist, self.playcount))

    def __repr__(self):
        return str(self.__dict__)

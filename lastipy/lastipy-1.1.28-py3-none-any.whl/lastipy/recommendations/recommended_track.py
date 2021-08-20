from lastipy.track import Track


class RecommendedTrack(Track):
    """Represents a recommended track, with a 'rating' value that can be used to determine it's 'strength'"""

    def __init__(self, track_name, artist, spotify_id=None, recommendation_rating=1):
        super().__init__(track_name, artist, spotify_id)
        self.recommendation_rating = recommendation_rating

    def __eq__(self, other):
        return (
            isinstance(other, RecommendedTrack)
            and self.track_name == other.track_name
            and self.artist == other.artist
            and self.spotify_id == other.spotify_id
            and self.recommendation_rating == other.recommendation_rating
        )

    def __hash__(self):
        return hash((self.track_name, self.artist, self.recommendation_rating))

    def __repr__(self):
        return str(self.__dict__)

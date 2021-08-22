"""API of Streaming URL."""
from operator import itemgetter

from showroompodcast.api import ShowroomApi


class StreamingUrl(ShowroomApi):
    """API of Streaming URL."""

    @classmethod
    def get_url_for_best_quality(cls, room_id: int):
        response = cls.request({"room_id": room_id})
        return sorted(response["streaming_url_list"], key=itemgetter("quality"), reverse=True)[0]["url"]

    @staticmethod
    def url():
        return "https://www.showroom-live.com/api/live/streaming_url"

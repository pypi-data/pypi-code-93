"""API of polling."""
from showroompodcast.api import ShowroomApi


class Polling(ShowroomApi):
    """API of polling."""

    @classmethod
    def poll(cls, room_id: int):
        """Returns True when on live, otherwise returns False."""
        response = cls.request({"room_id": room_id})
        return "live_end" not in response or response["live_end"] != 1

    @staticmethod
    def url():
        return "https://www.showroom-live.com/api/live/polling"

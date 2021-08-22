"""Stream spec factory."""
from logging import getLogger
from pathlib import Path

# noinspection PyPackageRequirements
import ffmpeg
from asyncffmpeg import StreamSpec

from showroompodcast.api.streaming_url import StreamingUrl
from showroompodcast.showroom_datetime import ShowroomDatetime

ENVIRONMENT_VALIABLE_KEY_AREA_ID = "RADIKO_AREA_ID"
AREA_ID_DEFAULT = "JP13"


class ShowroomStreamSpecFactory:
    """Stream spec factory."""

    def __init__(self, room_id: int):
        self.room_id = room_id
        self.logger = getLogger(__name__)

    async def create(self) -> StreamSpec:
        """Creates."""
        now = ShowroomDatetime.now_jst()
        now_string = ShowroomDatetime.encode(now)
        out_file_name = f"./output/{self.room_id}-{now_string}.mp4"
        self.logger.debug("out file name: %s", out_file_name)
        if Path(out_file_name).exists():
            self.logger.error("File already exists. out_file_name = %s", out_file_name)
            raise FileExistsError(f"File already exists. {out_file_name=}")
        streaming_url = StreamingUrl.get_url_for_best_quality(self.room_id)
        stream = ffmpeg.input(streaming_url, copytb="1")
        return ffmpeg.output(stream, out_file_name, f="mp4", c="copy")

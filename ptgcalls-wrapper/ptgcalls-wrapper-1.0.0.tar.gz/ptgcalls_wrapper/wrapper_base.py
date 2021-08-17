import hashlib
import os

from pytgcalls import PyTgCalls

from .exceptions import NotInCall


class WrapperBase:
    def __init__(
        self,
        pytgcalls: PyTgCalls,
        raw_dir: str = "./",
        ffmpeg: str = "ffmpeg",
        youtube_dl: str = "youtube-dl"
    ):
        self.pytgcalls = pytgcalls
        self.raw_dir = raw_dir
        self.ffmpeg = ffmpeg
        self.youtube_dl = youtube_dl

        if not os.path.isdir(raw_dir):
            os.mkdir(raw_dir)

    def _get_output(self, input: str) -> str:
        return os.path.join(self.raw_dir,  hashlib.md5(input.encode()).hexdigest())

    def _get_ffmpeg_cmd(self, input: str,  output: str) -> str:
        return f"{self.ffmpeg} -y -i {input} -f s16le -ac 1 -ar 48000 -acodec pcm_s16le {output}"

    def _get_youtube_dl_cmd(self, input: str) -> str:
        return f"{self.youtube_dl} -x -g \"{input}\""

    def _make_sure_in_call(self, chat_id: int):
        if chat_id not in self.pytgcalls.active_calls:
            raise NotInCall


__all__ = ["WrapperBase"]

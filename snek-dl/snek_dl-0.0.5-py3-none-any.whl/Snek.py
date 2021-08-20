import youtube_dl
from glob import glob
from typing import Union
from snek_dl.util import prettify
from subprocess import PIPE, Popen, SubprocessError


class Snek:
    def __init__(
        self,
        url: str,
        name_format: str = "",
        output_format: str = "",
        options: dict = None,
        headers: dict = None
    ):
        """
        :param url: URL of the video
        :param name_format: The output name of the video file
        ex) "%(uploader)s (%(uploader_id)s)/%(upload_date)s - %(title)s - [%(resolution)s] [%(id)s].%(ext)s"
        :param output_format: The output format of the video file
        ex) "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio"
        :param options: youtube-dl options dictionary (supersedes name_format and output_format)
        """
        self.url = url
        if not options:
            options = {}
            if name_format:
                options["outtmpl"] = name_format
            if output_format:
                options["format"] = output_format
        if headers:
            for k, v in headers.items():
                youtube_dl.utils.std_headers[k] = v
        self.engine = youtube_dl.YoutubeDL(options)

    @prettify
    def options(self) -> dict:
        return self.engine.params

    @prettify
    def download(self) -> dict:
        info = self.info(download=True)
        url = self._get_merged_video_url()
        temp_filename = self.engine.prepare_filename(info_dict=info).rsplit(".", 1)[0]
        final_filename = glob(f"{temp_filename}.*").pop()
        return dict(
            filename=final_filename,
            id=info["id"],
            urls=url,
            format=info["format"]
        )

    def _get_merged_video_url(self) -> dict:
        process = Popen(["youtube-dl", "--get-url", self.url], stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate()
        if stderr:
            raise SubprocessError(stderr)
        urls = stdout.decode("utf-8").split("\n")
        if len(urls) < 1:
            audio_url = urls[1]
        else:
            audio_url = None
        return dict(video_url=urls[0], audio_url=audio_url)

    @prettify
    def info(self, download: bool = False) -> dict:
        return self.engine.extract_info(url=self.url, download=download)

    @prettify
    def info_detail(self, detail: str):
        return self.info()[detail]

    @prettify
    def formats(self, full: bool = False) -> Union[dict, list]:
        format_info = self.info_detail("formats")
        if not full:
            video = list()
            audio = list()
            video_and_audio = list()
            for i in format_info:
                format_simple = dict(
                    format_id=i["format_id"],
                    format_note=i["format_note"],
                    ext=i["ext"],
                    filesize=i["filesize"],
                )
                if i["vcodec"] != "none" and i["acodec"] != "none":
                    video_and_audio.append(format_simple)
                elif i["vcodec"] != "none":
                    video.append(format_simple)
                elif i["acodec"] != "none":
                    audio.append(format_simple)
            format_info = dict(
                videos=video, audios=audio, video_and_audio=video_and_audio
            )
        return format_info

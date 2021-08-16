import time
from concurrent.futures import ThreadPoolExecutor
from pytube import YouTube

from .step import Step
from yt_concate.settings import VIDEOS_DIR


class DownloadVideos(Step):
    def process(self, data, inputs, utils, log):
        log.info("=== Downloading videos... ===")
        start = time.time()

        yt_set = set([found.yt for found in data])
        yt_ = []
        for yt in yt_set:
            if inputs["fast"]:
                if utils.video_file_exists(yt):
                    log.info(f"Found existing video file: {yt.id}, skipping.")
                    continue
                else:
                    yt_.append(yt)
            else:
                yt_.append(yt)

        if len(yt_) > 0:
            log.info(f"{len(yt_)} videos to be downloaded.")
            with ThreadPoolExecutor(max_workers=inputs["thread"]) as executor:
                for yt in yt_:
                    executor.submit(self.download_videos, yt, log)

        end = time.time()

        videos_amount = utils.file_amount(VIDEOS_DIR)
        log.info(f"Videos downloaded: Took {round(end-start, 2)} secs.")
        log.info(f"{videos_amount} video files in folder: {VIDEOS_DIR}.")
        return data

    @staticmethod
    def download_videos(yt, log):
        try:
            YouTube(yt.url).streams.first().download(output_path=VIDEOS_DIR, filename=yt.id + ".mp4")
            log.debug(f"Video downloading done: {yt.id}")
        except (KeyError, AttributeError):
            log.error(f"Error when downloading video: {yt.url}")

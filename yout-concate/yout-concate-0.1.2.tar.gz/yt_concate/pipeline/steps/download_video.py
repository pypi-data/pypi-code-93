import time
import concurrent.futures
from pytube import YouTube
from .step import Step
from yt_concate.settings import VIDEO_DIR
import logging

class DownloadVideo(Step):
    def process(self, inputs, utils, data):
        logger = logging.getLogger('record')
        start = time.perf_counter()
        yt_set = set([found.yt for found in data])
        yts = []
        for yt in list(yt_set):
            path = yt.get_video_filepath()
            if utils.check_video_file_exist(path):
                logger.warning(f'Video for : {yt.id} existed.')
                continue
            yts.append(yt)

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            executor.map(self.download_single_video, yts)

        end = time.perf_counter()
        logger.info(f'Video downloading elapsed time:{round(end - start, 2)} secs.')
        return data


    def download_single_video(self, yt):
        logger = logging.getLogger('record')
        try:
            logger.info(f'Downloading video : {yt.id}')
            name = f'{yt.id}.mp4'
            video = YouTube(yt.url)
            video.streams.first().download(VIDEO_DIR, filename=name)
        except:
            logger.warning(f'Video downloading error : {yt.id}')


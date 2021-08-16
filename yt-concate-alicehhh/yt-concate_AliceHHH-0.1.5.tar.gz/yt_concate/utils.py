import os
import shutil

from yt_concate.settings import DOWNLOADS_DIR
from yt_concate.settings import VIDEOS_DIR
from yt_concate.settings import CAPTIONS_DIR
from yt_concate.settings import OUTPUTS_DIR


class Utils:
    def __init__(self):
        pass

    # in Preflight
    @staticmethod
    def create_dirs():
        os.makedirs(DOWNLOADS_DIR, exist_ok=True)
        os.makedirs(VIDEOS_DIR, exist_ok=True)
        os.makedirs(CAPTIONS_DIR, exist_ok=True)
        os.makedirs(OUTPUTS_DIR, exist_ok=True)

    # in GetVideoList
    @staticmethod
    def get_video_list_filepath(channel_id):
        return os.path.join(DOWNLOADS_DIR, channel_id + ".txt")

    def video_list_file_exists(self, channel_id):
        path = self.get_video_list_filepath(channel_id)
        return os.path.exists(path) and os.path.getsize(path) > 0

    # in DownloadCaptions & DownloadVideos
    @staticmethod
    def caption_file_exists(yt):
        file_path = yt.caption_filepath
        return os.path.exists(file_path) and os.path.getsize(file_path) > 0

    @staticmethod
    def file_amount(folder_path):
        return len(os.walk(folder_path).__next__()[2])

    @staticmethod
    def video_file_exists(yt):
        file_path = yt.video_filepath
        return os.path.exists(file_path) and os.path.getsize(file_path) > 0

    # in EditVideo
    @staticmethod
    def get_output_filepath(channel_id, search_word):
        filename = f"{channel_id}_{search_word}.mp4"
        return os.path.join(OUTPUTS_DIR, filename)

    # in Postflight
    @staticmethod
    def delete_files(file_path):
        shutil.rmtree(file_path)

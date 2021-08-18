import os
from .settings import DOWNLOAD_DIR
from .settings import VIDEO_DIR
from .settings import CAPTION_DIR
from .settings import OUTPUT_DIR


class Utils:

    @staticmethod
    def create_downloads_dirs():
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)
        os.makedirs(VIDEO_DIR, exist_ok=True)
        os.makedirs(CAPTION_DIR, exist_ok=True)
        os.makedirs(OUTPUT_DIR, exist_ok=True)

    def get_video_list_path(self, channel_id):
        return os.path.join(DOWNLOAD_DIR, channel_id+'.txt')


    def check_video_list_exists(self, channel_id):
        path = self.get_video_list_path(channel_id)
        return os.path.exists(path) and os.path.getsize(path) > 0

    def check_caption_file_exist(self,path):
        return os.path.exists(path) and os.path.getsize(path) > 0

    def check_video_file_exist(self,path):
        return os.path.exists(path) and os.path.getsize(path) > 0







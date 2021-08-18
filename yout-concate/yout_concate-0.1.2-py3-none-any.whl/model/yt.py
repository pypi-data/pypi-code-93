import os
from yt_concate.settings import CAPTION_DIR
from yt_concate.settings import VIDEO_DIR


class Yt:
    def __init__(self, url):
        self.url = url
        self.id = self.get_video_id(self.url)
        self.caption = None

    def __str__(self):
        return f'<Video id:{self.id} , caption:{self.caption}>'

    def __repr__(self):
        return f'<Yt object -> id:{self.id} , caption:{self.caption}>'


    def get_video_id(self, url):
        return url.split("v=")[1]

    def get_caption_filepath(self):
        return os.path.join(CAPTION_DIR, self.id+'.txt')

    def get_video_filepath(self):
        return os.path.join(VIDEO_DIR, self.id+'.mp4')















import threading
import time
import subprocess
import pyautogui
import os
import glob
import cv2

from .store import Store


class ScreenRecorder( object ):
    def __init__(self, interval=1):
        self.interval = interval
        self.aThread = threading.Thread(target=self.take_screenshot )
        self.halt = False
        self.store = Store()

    def take_screenshot(self):
        while not self.halt:
            file_name = self.store.generate_file()
            pyautogui.screenshot( file_name )
            time.sleep( self.interval )

    def start(self):
        self.aThread.start()

    def stop(self):
        self.halt = True
        self.aThread.join()
        self.make_video()
        self.store.zip()

    def make_video(self):
        ffmpeg_glob = self.store.get_ffmpeg_glob()
        video_file_name_prefix = (os.path.join(self.store.get_dir_name(), self.store.get_guid()))
        video_file_name = '%s-video.avi' % (video_file_name_prefix)
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        nbr=0
        height = width = layers = 0
        video=None

        for file in glob.glob(ffmpeg_glob):
            if nbr == 0:
                frame = cv2.imread(file)
                height, width, layers = frame.shape
                video = cv2.VideoWriter(video_file_name, fourcc, 2, (width, height), True)
                video.write(cv2.imread(file))
            else:
                video.write(cv2.imread(file))

            nbr+=1

        video.release()
        self.store.add_file( video_file_name )
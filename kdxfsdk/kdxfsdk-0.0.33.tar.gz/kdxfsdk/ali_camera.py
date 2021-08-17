# -*- coding:utf-8 -*-
import os
import time
import numpy as np
from PIL import Image
import glob
from picamera.array import PiRGBArray
from picamera import PiCamera


class Camera(object):
    def __init__(self, resolution=(1024, 768), framerate=20):
        resolution = (resolution[1], resolution[0])
        # initialize the camera and stream
        self.camera = PiCamera()  # PiCamera gets resolution (height, width)
        self.camera.resolution = resolution
        self.camera.framerate = framerate
        print('PiCamera loaded...warming camera')
        time.sleep(2)

    def capture(self, file_name="tmp.jpg"):
        self.camera.capture(file_name)

    def shutdown(self):
        print('stoping PiCamera')
        time.sleep(.5)
        self.camera.close()


if __name__ == "__main__":
    camera = Camera()
    camera.capture("tmp.jpg")
    camera.shutdown()
